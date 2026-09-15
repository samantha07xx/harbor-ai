"""Deterministic pre-LLM agent orchestration.

Step 26 adds an agent-shaped orchestration layer. It chooses between safety
responses and the healthcare retrieval tool, but it does not call an LLM.
"""

from dataclasses import dataclass
from typing import Any

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
    ) -> None:
        self.safety_policy = safety_policy
        self.retrieval_tool = retrieval_tool

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

        tool_result = self.retrieval_tool.run(request.message, limit=1)
        return ChatResponse(
            answer=tool_result.answer,
            citations=tool_result.citations,
            suggested_followups=[
                "How do I apply for OHIP?",
                "What documents do I need for a health card?",
                "Can I get care before OHIP?",
            ],
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
