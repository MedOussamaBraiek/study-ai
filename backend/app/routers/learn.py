from uuid import uuid4
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.services.rag_service import retrieve_context
from app.services.llm_service import generate_questions_from_context
from app.agents.agent_state import build_agent, select_next_question

router = APIRouter()

AGENT = build_agent()

sessions = {}

# ------------------ REQUEST MODELS ------------------

class QuestionGenRequest(BaseModel):
    topic: str | None = None
    mode: str = "study"
    num_questions: int = 5 

class AnswerRequest(BaseModel):
    session_id: str
    user_answer: str


def normalize_question(q: dict):
    options = q.get("options")

    if not isinstance(options, list) or len(options) != 3:
        options = ["Option A", "Option B", "Option C"]

    correct = q.get("correct_answer")

    if correct not in options:
        correct = options[0]

    difficulty = q.get("difficulty")

    if difficulty not in ["easy", "medium", "hard"]:
        difficulty = "medium"

    return {
        "question": q.get("question") or "Fallback question",
        "options": options,
        "correct_answer": correct,
        "topic": q.get("topic") or "general",
        "difficulty": difficulty
    }

# ------------------ START SESSION ------------------

@router.post("/start-session")
async def start_session(data: QuestionGenRequest):

    num_q = min(max(data.num_questions, 1), 10)

    query = data.topic if data.topic else "key concepts"
    context, sources = retrieve_context(query)

    questions = generate_questions_from_context(context, num_q, data.mode)

    if not questions:
        raise HTTPException(status_code=500, detail="No questions generated")

    normalized_questions = [normalize_question(q) for q in questions]

    for i, q in enumerate(normalized_questions):
        q["id"] = i

    session_id = str(uuid4())

    sessions[session_id] = {
        "shown_ids": {0},
        "questions": normalized_questions,
        "current_index": 0,
        "score": 0,
        "answers": [],
        "topics": list(set([s["topic"] for s in sources])),
        "context": context,
        "weak_topics": {}
    }

    return {
        "session_id": session_id,
        "question": normalized_questions[0],
        "total_questions": len(normalized_questions),
    }

@router.post("/answer")
async def answer_question(data: AnswerRequest):


    session = sessions.get(data.session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    index = session["current_index"]
    question = session["questions"][index]


    agent_state = {
        "question": question["question"],
        "user_answer": data.user_answer,          
        "correct_answer": question["correct_answer"],  
        "difficulty": question.get("difficulty", "medium"),
        "is_correct": False,  
        "needs_explanation": False,
        "next_action": "",
        "topic": question.get("topic", "general"),
        "weak_topics": session["weak_topics"],
        "score": 0,
        "explanation": "",
    }

    result = AGENT.invoke(agent_state)

    is_correct = result["is_correct"]
    score = result.get("score", 0)
    explanation = result.get("explanation", None)
    action = result.get("next_action", "same_level")

    if not is_correct:
        topic = question.get("topic", "general")
        session["weak_topics"][topic] = session["weak_topics"].get(topic, 0) + 1

    evaluation = {
        "score": score,
        "is_correct": is_correct,
        "correct_answer": question["correct_answer"],
    }

    session["answers"].append({
        "question": question,
        "user_answer": data.user_answer,
        "evaluation": evaluation,
        "topic": question.get("topic"),
    })
    session["score"] += score
    session["current_index"] += 1

    if session["current_index"] >= len(session["questions"]):
        return {
            "done": True,
            "final_score": session["score"],
            "weak_topics": session["weak_topics"]
        }
    
    next_question = select_next_question(session, action)

    return {
        "done": False,
        "evaluation": evaluation,
        "next_question": next_question,
        "explanation": explanation,
    }