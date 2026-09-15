"""Chat API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.agent.answer_composer import AnswerComposer
from app.api.dependencies import get_answer_composer, get_rewritten_retrieval_service
from app.retrieval.service import RewrittenRetrievalService
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def create_chat_response(
    request: ChatRequest,
    service: Annotated[
        RewrittenRetrievalService,
        Depends(get_rewritten_retrieval_service),
    ],
    composer: Annotated[AnswerComposer, Depends(get_answer_composer)],
) -> ChatResponse:
    """Return a pre-agent local RAG response."""

    retrieval_result = service.retrieve(request.message, limit=1)
    draft_answer = composer.compose(retrieval_result)
    return ChatResponse(
        answer=draft_answer.answer,
        citations=draft_answer.citations,
        suggested_followups=[
            "How do I apply for OHIP?",
            "What documents do I need for a health card?",
            "Can I get care before OHIP?",
        ],
        metadata={
            "session_id": request.session_id,
            "implementation_status": "pre_agent_local_rag",
            "detected_intent": retrieval_result.rewrite.detected_intent,
            "rewrite_confidence": retrieval_result.rewrite.confidence,
            "needs_safety_check": retrieval_result.rewrite.needs_safety_check,
            "primary_query": retrieval_result.rewrite.primary_query,
            "retrieval_hit_count": len(retrieval_result.retrieval.hits),
            "user_context": request.user_context,
        },
    )
