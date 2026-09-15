"""Shared FastAPI dependencies."""

from app.agent.answer_composer import AnswerComposer
from app.retrieval.demo import get_local_demo_rewritten_retrieval_service
from app.retrieval.service import RewrittenRetrievalService


def get_rewritten_retrieval_service() -> RewrittenRetrievalService:
    """Return the current retrieval service dependency."""

    return get_local_demo_rewritten_retrieval_service()


def get_answer_composer() -> AnswerComposer:
    """Return the current answer composer dependency."""

    return AnswerComposer()
