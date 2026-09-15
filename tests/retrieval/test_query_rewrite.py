import pytest

from app.retrieval.query_rewrite import QueryIntent, QueryRewriteService


def test_rewrites_health_card_question_for_ohip_application() -> None:
    service = QueryRewriteService()

    result = service.rewrite("How do I get a health card?")

    assert result.detected_intent == QueryIntent.OHIP_APPLICATION
    assert result.primary_query == "Ontario apply for OHIP get health card required documents ServiceOntario"
    assert result.confidence == 0.86
    assert result.needs_safety_check is False


def test_rewrites_documents_question_with_official_terms() -> None:
    service = QueryRewriteService()

    result = service.rewrite("What papers do I need?")

    assert result.detected_intent == QueryIntent.REQUIRED_DOCUMENTS
    assert "proof of identity" in result.primary_query
    assert "immigration status" in result.primary_query


def test_rewrites_811_question_for_non_emergency_advice() -> None:
    service = QueryRewriteService()

    result = service.rewrite("Can I call someone if it is not an emergency?")

    assert result.detected_intent == QueryIntent.NON_EMERGENCY_ADVICE
    assert result.primary_query == "Ontario non-emergency health advice call 811 Health811"


def test_rewrites_newcomer_question_to_multiple_queries() -> None:
    service = QueryRewriteService()

    result = service.rewrite("I just landed and need a doctor. What can I do?")

    assert result.detected_intent == QueryIntent.NEWCOMER_HEALTHCARE_ACCESS
    assert result.primary_query == (
        "Ontario newcomer healthcare access before OHIP family doctor walk-in clinic"
    )
    assert len(result.rewritten_queries) == 3


def test_emergency_question_sets_safety_flag() -> None:
    service = QueryRewriteService()

    result = service.rewrite("I have chest pain, is this an emergency?")

    assert result.detected_intent == QueryIntent.EMERGENCY
    assert result.needs_safety_check is True


def test_unknown_question_falls_back_to_general_navigation() -> None:
    service = QueryRewriteService()

    result = service.rewrite("Where should I start?")

    assert result.detected_intent == QueryIntent.GENERAL_HEALTHCARE_NAVIGATION
    assert "Ontario healthcare navigation" in result.primary_query
    assert result.confidence == 0.45


def test_empty_question_is_rejected() -> None:
    service = QueryRewriteService()

    with pytest.raises(ValueError, match="empty"):
        service.rewrite("   ")
