"""Chat API routes."""

from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def create_chat_response(request: ChatRequest) -> ChatResponse:
    """Return a placeholder chat response until RAG is implemented."""

    return ChatResponse(
        answer=(
            "Harbor backend is running, but the agentic RAG chat pipeline is not "
            "implemented yet. This placeholder verifies the frontend and backend "
            "can communicate."
        ),
        citations=[],
        suggested_followups=[
            "How do I apply for OHIP?",
            "What documents do I need for a health card?",
        ],
        metadata={
            "session_id": request.session_id,
            "implementation_status": "backend_scaffold_only",
        },
    )
