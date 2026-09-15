"""Lightweight safety routing for Harbor chat."""

from dataclasses import dataclass
from enum import StrEnum


class SafetyRoute(StrEnum):
    """Supported safety routes before normal RAG answering."""

    PROCEED = "proceed"
    EMERGENCY = "emergency"
    OUT_OF_SCOPE = "out_of_scope"


@dataclass(frozen=True)
class SafetyAssessment:
    """Decision returned by the safety policy."""

    route: SafetyRoute
    message: str | None = None

    @property
    def should_continue(self) -> bool:
        """Return whether the normal local RAG path should continue."""

        return self.route == SafetyRoute.PROCEED


class SafetyPolicy:
    """Deterministic first-pass safety policy for the local MVP."""

    def assess(self, question: str) -> SafetyAssessment:
        """Assess whether a question should bypass the normal RAG path."""

        normalized_question = normalize_question(question)
        if not normalized_question:
            return SafetyAssessment(
                route=SafetyRoute.OUT_OF_SCOPE,
                message="Please ask a question about Ontario healthcare navigation.",
            )

        if is_emergency_question(normalized_question):
            return SafetyAssessment(
                route=SafetyRoute.EMERGENCY,
                message=(
                    "If this may be a medical emergency, call 911 or go to the nearest "
                    "emergency department. Harbor can help with general Ontario healthcare "
                    "navigation, but it cannot assess urgent symptoms."
                ),
            )

        if is_clear_out_of_scope_question(normalized_question):
            return SafetyAssessment(
                route=SafetyRoute.OUT_OF_SCOPE,
                message=(
                    "Harbor is focused on Ontario healthcare navigation. Try asking about "
                    "OHIP, health cards, Health811, walk-in clinics, finding a family doctor, "
                    "or getting care as a newcomer."
                ),
            )

        return SafetyAssessment(route=SafetyRoute.PROCEED)


def normalize_question(question: str) -> str:
    """Normalize text for deterministic matching."""

    return " ".join(question.lower().strip().split())


def is_emergency_question(normalized_question: str) -> bool:
    """Return whether the question contains emergency indicators."""

    non_emergency_phrases = (
        "not an emergency",
        "non emergency",
        "non-emergency",
    )
    if any(phrase in normalized_question for phrase in non_emergency_phrases):
        return False

    emergency_keywords = (
        "911",
        "emergency",
        "chest pain",
        "can't breathe",
        "cannot breathe",
        "stroke",
        "heart attack",
    )
    return any(keyword in normalized_question for keyword in emergency_keywords)


def is_clear_out_of_scope_question(normalized_question: str) -> bool:
    """Return whether the question is clearly outside Harbor's MVP scope."""

    in_scope_keywords = (
        "ohip",
        "health card",
        "healthcare",
        "health care",
        "health811",
        "811",
        "doctor",
        "clinic",
        "hospital",
        "nurse practitioner",
        "walk-in",
        "walk in",
        "family doctor",
        "ontario",
        "newcomer",
        "medical",
    )
    if any(keyword in normalized_question for keyword in in_scope_keywords):
        return False

    out_of_scope_keywords = (
        "weather",
        "stock",
        "crypto",
        "restaurant",
        "recipe",
        "homework",
        "python",
        "javascript",
        "movie",
        "music",
        "sports",
        "tax",
        "mortgage",
    )
    return any(keyword in normalized_question for keyword in out_of_scope_keywords)
