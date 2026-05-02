from uuid import uuid4
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.services.rag_service import retrieve_context
from app.services.llm_service import generate_questions_from_context
from app.agents.agent_state import app as learning_agent

router = APIRouter()

sessions = {}

# ------------------ REQUEST MODELS ------------------

class QuestionGenRequest(BaseModel):
    topic: str | None = None
    mode: str = "study"

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

    return {
        "question": q.get("question") or "Fallback question",
        "options": options,
        "correct_answer": correct,
        "topic": q.get("topic") or "general"
    }

# ------------------ START SESSION ------------------

@router.post("/start-session")
async def start_session(data: QuestionGenRequest):

    query = data.topic if data.topic else "key concepts"
    context, sources = retrieve_context(query)

    questions = generate_questions_from_context(context, 5, data.mode)

    if not questions:
        raise HTTPException(status_code=500, detail="No questions generated")

    normalized_questions = [normalize_question(q) for q in questions]

    session_id = str(uuid4())

    sessions[session_id] = {
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
        "question": normalized_questions[0]
    }

# ------------------ ANSWER LOOP ------------------
@router.post("/answer")
async def answer_question(data: AnswerRequest):

    session = sessions.get(data.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    index = session["current_index"]
    question = session["questions"][index]

    correct_answer = question.get("correct_answer")

    # ----------- EVALUATION (deterministic) -----------
    if data.user_answer.strip().lower() == correct_answer.strip().lower():
        evaluation = {
            "score": 10,
            "is_correct": True,
            "feedback": "Perfect! 🎯"
        }
    else:
        evaluation = {
            "score": 0,
            "is_correct": False,
            "feedback": f"Wrong. Correct answer: {correct_answer}"
        }

    # ----------- TRACK WEAK TOPICS -----------
    if evaluation["score"] < 5:
        topic = question.get("topic") or "general"

        session.setdefault("weak_topics", {})
        
        session["weak_topics"][topic] = session["weak_topics"].get(topic, 0) + 1

    # ----------- SAVE HISTORY -----------
    session["answers"].append({
        "question": question,
        "user_answer": data.user_answer,
        "evaluation": evaluation,
        "topic": question.get("topic")
    })

    session["score"] += evaluation["score"]
    session["current_index"] += 1

    # ----------- FINISH -----------
    if session["current_index"] >= len(session["questions"]):
        return {
            "done": True,
            "final_score": session["score"],
            "answers": session["answers"],
            "weak_topics": session["weak_topics"]
        }

    next_question = session["questions"][session["current_index"]]

    return {
        "done": False,
        "evaluation": evaluation,
        "next_question": next_question
    }

