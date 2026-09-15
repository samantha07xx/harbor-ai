"""API schemas for retrieval testing endpoints."""

from pydantic import BaseModel, Field

from app.retrieval.query_rewrite import QueryIntent
from app.schemas.chat import Citation
from app.schemas.chunks import RetrievalResult


class RetrievalSearchRequest(BaseModel):
    """Request body for the local retrieval search endpoint."""

    question: str = Field(min_length=1)
    limit: int = Field(default=6, ge=1, le=20)


class QueryRewriteMetadata(BaseModel):
    """Query rewrite metadata exposed by retrieval testing endpoints."""

    detected_intent: QueryIntent
    confidence: float = Field(ge=0.0, le=1.0)
    needs_safety_check: bool
    rewritten_queries: list[str]
    primary_query: str


class RetrievalSearchResponse(BaseModel):
    """Response body for a rewritten retrieval search."""

    original_question: str
    rewrite: QueryRewriteMetadata
    retrieval: RetrievalResult
    draft_answer: str
    citations: list[Citation] = Field(default_factory=list)
