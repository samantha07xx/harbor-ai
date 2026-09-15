"""Shared FastAPI dependencies."""

from app.agent.answer_composer import AnswerComposer
from app.agent.tools import HealthcareRetrievalTool
from app.retrieval.demo import get_local_demo_rewritten_retrieval_service
from app.retrieval.service import RewrittenRetrievalService
from app.safety.policy import SafetyPolicy


def get_rewritten_retrieval_service() -> RewrittenRetrievalService:
    """Return the current retrieval service dependency."""

    return get_local_demo_rewritten_retrieval_service()


def get_answer_composer() -> AnswerComposer:
    """Return the current answer composer dependency."""

    return AnswerComposer()


def get_safety_policy() -> SafetyPolicy:
    """Return the current safety policy dependency."""

    return SafetyPolicy()


def get_healthcare_retrieval_tool() -> HealthcareRetrievalTool:
    """Return the current agent-facing healthcare retrieval tool."""

    return HealthcareRetrievalTool(
        retrieval_service=get_rewritten_retrieval_service(),
        answer_composer=get_answer_composer(),
    )
