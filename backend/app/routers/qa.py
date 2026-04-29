from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.services.rag_service import retrieve_context
import app.services.vector_store as vector_store
from app.services.llm_service import generate_answer, generate_questions_from_context

class QuestionRequest(BaseModel):
    question: str

class QuestionGenRequest(BaseModel):
    topic: str | None = None
    num_questions: int = 5
    mode: str = "study"


router = APIRouter()

@router.post("/ask")
async def ask_question(data: QuestionRequest):
    question = data.question

    if vector_store.index is None:
        raise HTTPException(
            status_code=400,
            detail="Upload a PDF first"
        )

    context, sources = retrieve_context(question)

    if not sources:
        raise HTTPException(
            status_code=404,
            detail="No relevant information found in the document."
        )

    answer = generate_answer(context, question)

    return {
        "answer": answer,
        "sources": sources,
        "topics": list(set([s["topic"] for s in sources]))
    }

@router.post("/generate-questions")
async def generate_questions(data: QuestionGenRequest):
    context, sources = retrieve_context(data.topic if data.topic else "summarize key concepts")

    questions = generate_questions_from_context(context, data.num_questions, data.mode)

    return {
        "questions": questions,
        "sources": sources
    }

