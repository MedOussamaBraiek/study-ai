from uuid import uuid4
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.services.rag_service import retrieve_context
from app.services.llm_service import generate_questions_from_context
from app.services.llm_service import evaluate_answer
from app.agents.agent_state import app as learning_agent

class QuestionGenRequest(BaseModel):
    topic: str | None = None
    num_questions: int = 5
    mode: str = "study"

class AnswerRequest(BaseModel):
    session_id: str
    user_answer: str

router = APIRouter()

sessions = {}

@router.post("/start-session")
async def start_session(data: QuestionGenRequest):
     
     query = data.topic if data.topic else "key concepts"
     context, sources = retrieve_context(query)

     questions = generate_questions_from_context(context, data.num_questions, data.mode)

     session_id = str(uuid4())

     sessions[session_id] = {
        "questions": questions,
        "current_index": 0,
        "score": 0,
        "answers": [],
        "topics": list(set([s["topic"] for s in sources])),
        "context": context
    }
     
     return {
        "session_id": session_id,
        "first_question": questions[0]
    }

@router.post("/answer")
async def answer_question(data: AnswerRequest):

    session = sessions.get(data.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    index = session["current_index"]
    question = session["questions"][index]

    result = learning_agent.invoke({
        "question": question["question"],
        "user_answer": data.user_answer
    })

    evaluation = result["evaluation"]
    action = result["next_action"]

    if evaluation.get("score", 0) < 5:
        topic = question.get("topic")

        session.setdefault("weak_topics", {})
        session["weak_topics"][topic] = session["weak_topics"].get(topic, 0) + 1

    session["answers"].append({
        "question": question,
        "user_answer": data.user_answer,
        "evaluation": evaluation,
        "topic": question.get("topic")
    })

    session["score"] += evaluation.get("score", 0)
    session["current_index"] += 1

    if session["current_index"] >= len(session["questions"]):
        return {
            "done": True,
            "final_score": session["score"],
            "answers": session["answers"]
        }
    
    next_question = session["questions"][session["current_index"]]

    return {
        "done": False,
        "evaluation": evaluation,
        "next_question": next_question
    }