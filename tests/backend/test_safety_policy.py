from app.safety.policy import SafetyPolicy, SafetyRoute


def test_safety_policy_allows_non_emergency_healthcare_question() -> None:
    assessment = SafetyPolicy().assess("Can I call someone if it is not an emergency?")

    assert assessment.route == SafetyRoute.PROCEED
    assert assessment.should_continue is True


def test_safety_policy_routes_emergency_question() -> None:
    assessment = SafetyPolicy().assess("I have chest pain and cannot breathe")

    assert assessment.route == SafetyRoute.EMERGENCY
    assert assessment.should_continue is False
    assert assessment.message is not None
    assert "call 911" in assessment.message


def test_safety_policy_routes_clear_out_of_scope_question() -> None:
    assessment = SafetyPolicy().assess("What is the weather tomorrow?")

    assert assessment.route == SafetyRoute.OUT_OF_SCOPE
    assert assessment.should_continue is False
    assert assessment.message is not None
    assert "Ontario healthcare navigation" in assessment.message


def test_safety_policy_rejects_empty_question() -> None:
    assessment = SafetyPolicy().assess("   ")

    assert assessment.route == SafetyRoute.OUT_OF_SCOPE
    assert assessment.should_continue is False
