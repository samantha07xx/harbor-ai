from app.evaluation.run_eval import (
    GoldenQuestion,
    build_default_agent,
    evaluate_case,
    load_golden_questions,
    run_evaluation,
)


def test_load_golden_questions_has_unique_ids() -> None:
    questions = load_golden_questions()

    question_ids = [question.id for question in questions]
    assert len(questions) >= 5
    assert len(question_ids) == len(set(question_ids))


def test_golden_questions_pass_against_deterministic_agent() -> None:
    summary = run_evaluation()

    assert summary.passed is True
    assert summary.passed_count == summary.total_count


def test_evaluate_case_reports_failures() -> None:
    agent = build_default_agent()
    result = evaluate_case(
        agent,
        GoldenQuestion(
            id="intent_failure",
            question="Can I call someone if it is not an emergency?",
            expected_safety_route="proceed",
            expected_intent="ohip_application",
            expected_citation_titles=["Health811"],
            expected_answer_contains=["Health811"],
        ),
    )

    assert result.passed is False
    assert result.failures
    assert "expected intent" in result.failures[0]
