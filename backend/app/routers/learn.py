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

# ------------------ START SESSION ------------------

@router.post("/start-session")
async def start_session(data: QuestionGenRequest):
     
     query = data.topic if data.topic else "key concepts"
     context, sources = retrieve_context(query)

     questions = generate_questions_from_context(context, 1, data.mode)

     if not questions:
        raise HTTPException(status_code=500, detail="No questions generated")

     first_question = questions[0]

     session_id = str(uuid4())

     sessions[session_id] = {
        "current_question": first_question,
        "score": 0,
        "answers": [],
        "topics": list(set([s["topic"] for s in sources])),
        "context": context,
        "weak_topics": {}
    }
     
     return {
        "session_id": session_id,
        "question": questions[0]
    }

# ------------------ ANSWER LOOP ------------------

@router.post("/answer")
async def answer_question(data: AnswerRequest):

    session = sessions.get(data.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    question = session["current_question"]

    # AGENT CALL
    result = learning_agent.invoke({
        "question": question["question"],
        "user_answer": data.user_answer,
        "topic": question.get("topic"),
        "context": session.get("context"),
        "weak_topics": session.get("weak_topics", {})
    })

    evaluation = result["evaluation"]

    if not isinstance(evaluation, dict):
        evaluation = {
            "score": 0,
            "feedback": "Evaluation failed",
            "is_correct": False
        }

    explanation = result.get("explanation", None)

    next_question = {
        "question": result["question"],
        "options": result.get("options", []),
        "topic": result["topic"]
    }

    # TRACK WEAK TOPICS
    if evaluation.get("score", 0) < 5:
        topic = question.get("topic")
        session["weak_topics"][topic] = session["weak_topics"].get(topic, 0) + 1

    # SAVE HISTORY
    session["answers"].append({
        "question": question,
        "user_answer": data.user_answer,
        "evaluation": evaluation,
        "topic": question.get("topic")
    })

    session["score"] += evaluation.get("score", 0)

    session["current_question"] = next_question

    if len(session["answers"]) >= 2:
        return {
            "done": True,
            "final_score": session["score"],
            "answers": session["answers"],
            "weak_topics": session["weak_topics"]
    }
    
    return {
        "done": False,
        "evaluation": evaluation,
        "explanation": explanation,
        "next_question": next_question
    }