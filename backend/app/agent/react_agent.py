"""Agent orchestration for Harbor safety, planning, and retrieval."""

from dataclasses import dataclass
from typing import Any

from app.agent.planner import AgentPlanner, AgentPlanRequest, AgentPlanRoute
from app.agent.tools import HealthcareRetrievalTool
from app.safety.policy import SafetyPolicy
from app.schemas.chat import ChatResponse


@dataclass(frozen=True)
class AgentTurnRequest:
    """Input for one local agent turn."""

    message: str
    session_id: str | None = None
    user_context: dict[str, Any] | None = None


class DeterministicHealthcareAgent:
    """Small deterministic agent that routes safety or retrieval."""

    def __init__(
        self,
        *,
        safety_policy: SafetyPolicy,
        retrieval_tool: HealthcareRetrievalTool,
        planner: AgentPlanner | None = None,
    ) -> None:
        self.safety_policy = safety_policy
        self.retrieval_tool = retrieval_tool
        self.planner = planner

    def run_turn(self, request: AgentTurnRequest) -> ChatResponse:
        """Run one safety-gated local healthcare navigation turn."""

        user_context = request.user_context or {}
        safety_assessment = self.safety_policy.assess(request.message)
        if not safety_assessment.should_continue:
            return ChatResponse(
                answer=str(safety_assessment.message),
                citations=[],
                suggested_followups=[
                    "How do I apply for OHIP?",
                    "What documents do I need for a health card?",
                    "Can I call Health811 for non-emergency advice?",
                ],
                metadata={
                    "session_id": request.session_id,
                    "implementation_status": "deterministic_agent_safety",
                    "agent_mode": "deterministic_pre_llm",
                    "safety_route": safety_assessment.route,
                    "user_context": user_context,
                },
            )

        if self.planner is not None:
            plan = self.planner.plan(
                AgentPlanRequest(
                    message=request.message,
                    user_context=user_context,
                )
            )
            if plan.route != AgentPlanRoute.RETRIEVE:
                return ChatResponse(
                    answer=plan.message or fallback_message_for_plan_route(plan.route),
                    citations=[],
                    suggested_followups=suggested_healthcare_followups(),
                    metadata={
                        "session_id": request.session_id,
                        "implementation_status": f"openai_agent_{plan.route}",
                        "agent_mode": "openai_react_planner",
                        "safety_route": safety_assessment.route,
                        "planner_route": plan.route,
                        "planner_model": self.planner.model,
                        "planner_rationale": plan.rationale,
                        "user_context": user_context,
                    },
                )

            tool_question = plan.retrieval_question or request.message
            tool_result = self.retrieval_tool.run(tool_question, limit=3)
            return ChatResponse(
                answer=tool_result.answer,
                citations=tool_result.citations,
                suggested_followups=suggested_healthcare_followups(),
                metadata={
                    "session_id": request.session_id,
                    "implementation_status": "openai_agent_tool_rag",
                    "agent_mode": "openai_react_planner",
                    "safety_route": safety_assessment.route,
                    "planner_route": plan.route,
                    "planner_model": self.planner.model,
                    "planner_rationale": plan.rationale,
                    "tool_question": tool_question,
                    "tool_name": tool_result.tool_name,
                    **tool_result.metadata,
                    "user_context": user_context,
                },
            )

        tool_result = self.retrieval_tool.run(request.message, limit=1)
        return ChatResponse(
            answer=tool_result.answer,
            citations=tool_result.citations,
            suggested_followups=suggested_healthcare_followups(),
            metadata={
                "session_id": request.session_id,
                "implementation_status": "deterministic_agent_local_rag",
                "agent_mode": "deterministic_pre_llm",
                "safety_route": safety_assessment.route,
                "tool_name": tool_result.tool_name,
                **tool_result.metadata,
                "user_context": user_context,
            },
        )


def suggested_healthcare_followups() -> list[str]:
    """Return default healthcare follow-up suggestions."""

    return [
        "How do I apply for OHIP?",
        "What documents do I need for a health card?",
        "Can I get care before OHIP?",
    ]


def fallback_message_for_plan_route(route: AgentPlanRoute) -> str:
    """Return a fallback user-facing message for a non-retrieval plan."""

    match route:
        case AgentPlanRoute.CLARIFY:
            return "Could you share a little more detail about what Ontario healthcare help you need?"
        case AgentPlanRoute.DIRECT_ANSWER:
            return "I can help with Ontario healthcare navigation questions."
        case AgentPlanRoute.OUT_OF_SCOPE:
            return (
                "Harbor is focused on Ontario healthcare navigation. Try asking about OHIP, "
                "health cards, Health811, walk-in clinics, or finding a family doctor."
            )
        case AgentPlanRoute.SAFETY:
            return (
                "If this may be a medical emergency, call 911 or go to the nearest emergency "
                "department."
            )
        case AgentPlanRoute.RETRIEVE:
            return "I will look for the most relevant trusted Ontario healthcare source."
