from pydantic import BaseModel
from fastapi import APIRouter
from app.services.llm_service import evaluate_answer

class EvaluateRequest(BaseModel):
    question: str
    user_answer: str
    correct_answer: str | None = None
    context: str | None = None

router = APIRouter()

@router.post("/evaluate-answer")
async def evaluate_answer_route(data: EvaluateRequest):
    
    result = evaluate_answer(
    data.question,
    data.user_answer,
    data.correct_answer,
    data.context
)

    return {
        "evaluation": result
    }