"""Agent tool boundaries.

Step 25 adds a stable local retrieval tool. It does not introduce LLM reasoning;
it gives the future agent a narrow interface for calling Harbor retrieval.
"""

from dataclasses import dataclass
from typing import Any

from app.agent.answer_composer import AnswerComposer
from app.retrieval.service import RewrittenRetrievalService
from app.schemas.chat import Citation


@dataclass(frozen=True)
class AgentToolResult:
    """Result returned by an agent-facing tool."""

    tool_name: str
    answer: str
    citations: list[Citation]
    metadata: dict[str, Any]


class HealthcareRetrievalTool:
    """Agent-facing tool for local healthcare retrieval and cited drafting."""

    name = "healthcare_retrieval"
    description = (
        "Rewrite an Ontario healthcare navigation question, retrieve trusted source chunks, "
        "and return a conservative cited draft answer."
    )

    def __init__(
        self,
        *,
        retrieval_service: RewrittenRetrievalService,
        answer_composer: AnswerComposer,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.answer_composer = answer_composer

    def run(self, question: str, *, limit: int = 3) -> AgentToolResult:
        """Run local retrieval and answer drafting for one question."""

        retrieval_result = self.retrieval_service.retrieve(question, limit=limit)
        draft_answer = self.answer_composer.compose(retrieval_result)
        return AgentToolResult(
            tool_name=self.name,
            answer=draft_answer.answer,
            citations=draft_answer.citations,
            metadata={
                "retrieval_corpus_mode": self.retrieval_service.corpus_mode,
                "detected_intent": retrieval_result.rewrite.detected_intent,
                "rewrite_confidence": retrieval_result.rewrite.confidence,
                "needs_safety_check": retrieval_result.rewrite.needs_safety_check,
                "primary_query": retrieval_result.rewrite.primary_query,
                "rewritten_queries": retrieval_result.rewrite.rewritten_queries,
                "retrieval_hit_count": len(retrieval_result.retrieval.hits),
                "answer_mode": draft_answer.answer_mode,
                "llm_model": draft_answer.llm_model,
            },
        )
