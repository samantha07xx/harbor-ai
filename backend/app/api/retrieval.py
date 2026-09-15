"""Retrieval API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.retrieval.demo import get_local_demo_rewritten_retrieval_service
from app.retrieval.service import RewrittenRetrievalResult, RewrittenRetrievalService
from app.schemas.retrieval import (
    QueryRewriteMetadata,
    RetrievalSearchRequest,
    RetrievalSearchResponse,
)

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


def get_rewritten_retrieval_service() -> RewrittenRetrievalService:
    """Return the current retrieval service dependency."""

    return get_local_demo_rewritten_retrieval_service()


@router.post("/search", response_model=RetrievalSearchResponse)
def search_retrieval(
    request: RetrievalSearchRequest,
    service: Annotated[
        RewrittenRetrievalService,
        Depends(get_rewritten_retrieval_service),
    ],
) -> RetrievalSearchResponse:
    """Rewrite a question and return retrieved chunks for local testing."""

    result = service.retrieve(request.question, limit=request.limit)
    return map_rewritten_retrieval_result(result)


def map_rewritten_retrieval_result(
    result: RewrittenRetrievalResult,
) -> RetrievalSearchResponse:
    """Map the internal retrieval composition result to the API response."""

    return RetrievalSearchResponse(
        original_question=result.original_question,
        rewrite=QueryRewriteMetadata(
            detected_intent=result.rewrite.detected_intent,
            confidence=result.rewrite.confidence,
            needs_safety_check=result.rewrite.needs_safety_check,
            rewritten_queries=result.rewrite.rewritten_queries,
            primary_query=result.rewrite.primary_query,
        ),
        retrieval=result.retrieval,
    )
