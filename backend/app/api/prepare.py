from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class PrepareRequest(BaseModel):
    question: str
    language: str = "en"


@router.post("/prepare")
def prepare_visit(request: PrepareRequest):
    return {
        "answer": "Prepare API is connected. RAG response will be added later.",
        "question": request.question,
        "language": request.language,
        "sources": [],
    }