"""Shared FastAPI dependencies."""

from app.agent.answer_composer import AnswerComposer
from app.agent.llm import OpenAIAnswerProvider
from app.agent.planner import AgentPlanner, OpenAIReActPlanner
from app.agent.react_agent import DeterministicHealthcareAgent
from app.agent.tools import HealthcareRetrievalTool
from app.config import get_settings
from app.retrieval.demo import get_local_demo_rewritten_retrieval_service
from app.retrieval.live import get_live_or_demo_rewritten_retrieval_service
from app.retrieval.qdrant import get_qdrant_rewritten_retrieval_service
from app.retrieval.service import RewrittenRetrievalService
from app.safety.policy import SafetyPolicy


def get_rewritten_retrieval_service() -> RewrittenRetrievalService:
    """Return the current retrieval service dependency."""

    retrieval_mode = get_settings().retrieval_mode.lower()
    if retrieval_mode == "qdrant":
        return get_qdrant_rewritten_retrieval_service()
    if retrieval_mode == "live":
        return get_live_or_demo_rewritten_retrieval_service()
    return get_local_demo_rewritten_retrieval_service()


def get_answer_composer() -> AnswerComposer:
    """Return the current answer composer dependency."""

    settings = get_settings()
    if settings.answer_provider.lower() == "openai":
        return AnswerComposer(
            OpenAIAnswerProvider(
                api_key=settings.openai_api_key or "",
                model=settings.llm_model,
                base_url=settings.openai_base_url,
            )
        )
    return AnswerComposer()


def get_safety_policy() -> SafetyPolicy:
    """Return the current safety policy dependency."""

    return SafetyPolicy()


def get_agent_planner() -> AgentPlanner | None:
    """Return the configured ReAct-style planner if enabled."""

    settings = get_settings()
    if settings.agent_provider.lower() == "openai":
        return OpenAIReActPlanner(
            api_key=settings.openai_api_key or "",
            model=settings.llm_model,
            base_url=settings.openai_base_url,
        )
    return None


def get_healthcare_retrieval_tool() -> HealthcareRetrievalTool:
    """Return the current agent-facing healthcare retrieval tool."""

    return HealthcareRetrievalTool(
        retrieval_service=get_rewritten_retrieval_service(),
        answer_composer=get_answer_composer(),
    )


def get_deterministic_healthcare_agent() -> DeterministicHealthcareAgent:
    """Return the deterministic pre-LLM healthcare agent."""

    return DeterministicHealthcareAgent(
        safety_policy=get_safety_policy(),
        retrieval_tool=get_healthcare_retrieval_tool(),
        planner=get_agent_planner(),
    )
