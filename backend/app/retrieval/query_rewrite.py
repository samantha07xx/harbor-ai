"""Deterministic query rewrite for MVP retrieval tests.

Step 19 adds a lightweight rewrite boundary. It does not call an LLM.
"""

from dataclasses import dataclass
from enum import StrEnum


class QueryIntent(StrEnum):
    """Supported deterministic query rewrite intents."""

    OHIP_APPLICATION = "ohip_application"
    OHIP_ELIGIBILITY = "ohip_eligibility"
    REQUIRED_DOCUMENTS = "required_documents"
    FINDING_FAMILY_DOCTOR = "finding_family_doctor"
    WALK_IN_CLINIC = "walk_in_clinic"
    NON_EMERGENCY_ADVICE = "non_emergency_advice"
    NEWCOMER_HEALTHCARE_ACCESS = "newcomer_healthcare_access"
    EMERGENCY = "emergency"
    GENERAL_HEALTHCARE_NAVIGATION = "general_healthcare_navigation"


@dataclass(frozen=True)
class QueryRewriteResult:
    """Search-ready rewrite output."""

    original_question: str
    rewritten_queries: list[str]
    detected_intent: QueryIntent
    confidence: float
    needs_safety_check: bool = False

    @property
    def primary_query(self) -> str:
        """Return the first rewritten query."""

        return self.rewritten_queries[0]


@dataclass(frozen=True)
class RewriteRule:
    """Keyword-based deterministic rewrite rule."""

    intent: QueryIntent
    keywords: tuple[str, ...]
    rewritten_queries: tuple[str, ...]
    confidence: float
    needs_safety_check: bool = False


class QueryRewriteService:
    """Rewrite user questions into retrieval-friendly Ontario healthcare queries."""

    def __init__(self, rules: list[RewriteRule] | None = None) -> None:
        self.rules = rules or DEFAULT_REWRITE_RULES

    def rewrite(self, question: str) -> QueryRewriteResult:
        """Rewrite a user question using deterministic MVP rules."""

        normalized_question = normalize_question(question)
        if not normalized_question:
            raise ValueError("Question cannot be empty")

        for rule in self.rules:
            if any(keyword in normalized_question for keyword in rule.keywords):
                return QueryRewriteResult(
                    original_question=question,
                    rewritten_queries=list(rule.rewritten_queries),
                    detected_intent=rule.intent,
                    confidence=rule.confidence,
                    needs_safety_check=rule.needs_safety_check,
                )

        return QueryRewriteResult(
            original_question=question,
            rewritten_queries=(
                [
                    "Ontario healthcare navigation OHIP health card Health811 family doctor walk-in clinic"
                ]
            ),
            detected_intent=QueryIntent.GENERAL_HEALTHCARE_NAVIGATION,
            confidence=0.45,
            needs_safety_check=False,
        )


def normalize_question(question: str) -> str:
    """Normalize a question for simple keyword matching."""

    return " ".join(question.lower().strip().split())


DEFAULT_REWRITE_RULES = [
    RewriteRule(
        intent=QueryIntent.NON_EMERGENCY_ADVICE,
        keywords=("811", "health811", "non-emergency", "non emergency", "call someone"),
        rewritten_queries=(
            "Ontario non-emergency health advice call 811 Health811",
        ),
        confidence=0.88,
    ),
    RewriteRule(
        intent=QueryIntent.EMERGENCY,
        keywords=("emergency", "911", "chest pain", "can't breathe", "cannot breathe"),
        rewritten_queries=(
            "Ontario emergency healthcare call 911 emergency department urgent medical help",
        ),
        confidence=0.9,
        needs_safety_check=True,
    ),
    RewriteRule(
        intent=QueryIntent.NEWCOMER_HEALTHCARE_ACCESS,
        keywords=("newcomer", "just moved", "just landed", "new to ontario", "without ohip"),
        rewritten_queries=(
            "Ontario newcomer healthcare access before OHIP family doctor walk-in clinic",
            "Ontario apply for OHIP health card newcomer eligibility",
            "Ontario non emergency medical advice Health811",
        ),
        confidence=0.78,
    ),
    RewriteRule(
        intent=QueryIntent.REQUIRED_DOCUMENTS,
        keywords=("documents", "papers", "proof of", "bring", "id"),
        rewritten_queries=(
            "Ontario documents needed to get a health card OHIP proof of identity residency citizenship immigration status",
        ),
        confidence=0.86,
    ),
    RewriteRule(
        intent=QueryIntent.FINDING_FAMILY_DOCTOR,
        keywords=("family doctor", "doctor", "nurse practitioner", "health care connect"),
        rewritten_queries=(
            "Ontario find a family doctor Health Care Connect official",
        ),
        confidence=0.82,
    ),
    RewriteRule(
        intent=QueryIntent.WALK_IN_CLINIC,
        keywords=("walk-in", "walk in", "clinic", "see a doctor without appointment"),
        rewritten_queries=(
            "Ontario walk-in clinic healthcare access without family doctor",
        ),
        confidence=0.8,
    ),
    RewriteRule(
        intent=QueryIntent.OHIP_ELIGIBILITY,
        keywords=("eligible", "eligibility", "qualify", "coverage", "covered"),
        rewritten_queries=(
            "Ontario OHIP eligibility health coverage newcomer requirements",
        ),
        confidence=0.82,
    ),
    RewriteRule(
        intent=QueryIntent.OHIP_APPLICATION,
        keywords=("apply", "health card", "ohip card", "get ohip", "get a card"),
        rewritten_queries=(
            "Ontario apply for OHIP get health card required documents ServiceOntario",
        ),
        confidence=0.86,
    ),
]
