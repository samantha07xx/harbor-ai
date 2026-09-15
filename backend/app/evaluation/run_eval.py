"""Deterministic local evaluation runner."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field

from app.agent.answer_composer import AnswerComposer
from app.agent.react_agent import AgentTurnRequest, DeterministicHealthcareAgent
from app.agent.tools import HealthcareRetrievalTool
from app.retrieval.demo import get_local_demo_rewritten_retrieval_service
from app.safety.policy import SafetyPolicy

DEFAULT_GOLDEN_QUESTIONS_PATH = Path(__file__).with_name("golden_questions.json")


class GoldenQuestion(BaseModel):
    """Expected behavior for one evaluation question."""

    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    expected_safety_route: str
    expected_intent: str | None = None
    expected_citation_titles: list[str] = Field(default_factory=list)
    expected_answer_contains: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class EvaluationCaseResult:
    """Result for one golden question."""

    id: str
    passed: bool
    failures: list[str]


@dataclass(frozen=True)
class EvaluationSummary:
    """Aggregate result for a deterministic evaluation run."""

    results: list[EvaluationCaseResult]

    @property
    def passed(self) -> bool:
        """Return whether all evaluation cases passed."""

        return all(result.passed for result in self.results)

    @property
    def passed_count(self) -> int:
        """Return the number of passing cases."""

        return sum(1 for result in self.results if result.passed)

    @property
    def total_count(self) -> int:
        """Return the total number of cases."""

        return len(self.results)


def load_golden_questions(path: Path = DEFAULT_GOLDEN_QUESTIONS_PATH) -> list[GoldenQuestion]:
    """Load golden questions from disk."""

    records = json.loads(path.read_text(encoding="utf-8"))
    return [GoldenQuestion.model_validate(record) for record in records]


def build_default_agent() -> DeterministicHealthcareAgent:
    """Build the local deterministic agent used by evaluation."""

    return DeterministicHealthcareAgent(
        safety_policy=SafetyPolicy(),
        retrieval_tool=HealthcareRetrievalTool(
            retrieval_service=get_local_demo_rewritten_retrieval_service(),
            answer_composer=AnswerComposer(),
        ),
    )


def evaluate_case(
    agent: DeterministicHealthcareAgent,
    question: GoldenQuestion,
) -> EvaluationCaseResult:
    """Evaluate one golden question against the deterministic agent."""

    response = agent.run_turn(
        AgentTurnRequest(
            session_id=f"eval-{question.id}",
            message=question.question,
            user_context={"province": "Ontario"},
        )
    )
    failures: list[str] = []

    actual_safety_route = response.metadata.get("safety_route")
    if actual_safety_route != question.expected_safety_route:
        failures.append(
            f"expected safety_route {question.expected_safety_route!r}, got {actual_safety_route!r}"
        )

    actual_intent = response.metadata.get("detected_intent")
    if actual_intent != question.expected_intent:
        failures.append(f"expected intent {question.expected_intent!r}, got {actual_intent!r}")

    actual_citation_titles = [citation.title for citation in response.citations]
    if actual_citation_titles != question.expected_citation_titles:
        failures.append(
            "expected citation titles "
            f"{question.expected_citation_titles!r}, got {actual_citation_titles!r}"
        )

    answer_lower = response.answer.lower()
    for expected_text in question.expected_answer_contains:
        if expected_text.lower() not in answer_lower:
            failures.append(f"expected answer to contain {expected_text!r}")

    return EvaluationCaseResult(
        id=question.id,
        passed=not failures,
        failures=failures,
    )


def run_evaluation(
    *,
    path: Path = DEFAULT_GOLDEN_QUESTIONS_PATH,
    agent: DeterministicHealthcareAgent | None = None,
) -> EvaluationSummary:
    """Run all deterministic golden questions."""

    questions = load_golden_questions(path)
    evaluation_agent = agent or build_default_agent()
    return EvaluationSummary(
        results=[evaluate_case(evaluation_agent, question) for question in questions],
    )


def main() -> int:
    """Run evaluation from the command line."""

    summary = run_evaluation()
    for result in summary.results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status} {result.id}")
        for failure in result.failures:
            print(f"  - {failure}")

    print(f"{summary.passed_count}/{summary.total_count} golden questions passed")
    return 0 if summary.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
