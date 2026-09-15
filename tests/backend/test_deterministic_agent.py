from app.agent.answer_composer import AnswerComposer
from app.agent.react_agent import AgentTurnRequest, DeterministicHealthcareAgent
from app.agent.tools import HealthcareRetrievalTool
from app.retrieval.demo import get_local_demo_rewritten_retrieval_service
from app.safety.policy import SafetyPolicy


def make_agent() -> DeterministicHealthcareAgent:
    return DeterministicHealthcareAgent(
        safety_policy=SafetyPolicy(),
        retrieval_tool=HealthcareRetrievalTool(
            retrieval_service=get_local_demo_rewritten_retrieval_service(),
            answer_composer=AnswerComposer(),
        ),
    )


def test_agent_routes_healthcare_question_to_retrieval_tool() -> None:
    agent = make_agent()

    response = agent.run_turn(
        AgentTurnRequest(
            session_id="test-session",
            message="Can I call someone if it is not an emergency?",
            user_context={"province": "Ontario"},
        )
    )

    assert "Health811" in response.answer
    assert response.citations[0].title == "Health811"
    assert response.metadata["implementation_status"] == "deterministic_agent_local_rag"
    assert response.metadata["agent_mode"] == "deterministic_pre_llm"
    assert response.metadata["safety_route"] == "proceed"
    assert response.metadata["tool_name"] == "healthcare_retrieval"


def test_agent_routes_emergency_question_to_safety_response() -> None:
    agent = make_agent()

    response = agent.run_turn(
        AgentTurnRequest(
            session_id="test-session",
            message="I have chest pain and cannot breathe",
            user_context={"province": "Ontario"},
        )
    )

    assert response.answer.startswith("If this may be a medical emergency")
    assert response.citations == []
    assert response.metadata["implementation_status"] == "deterministic_agent_safety"
    assert response.metadata["safety_route"] == "emergency"


def test_agent_routes_out_of_scope_question_to_safety_response() -> None:
    agent = make_agent()

    response = agent.run_turn(
        AgentTurnRequest(
            session_id="test-session",
            message="What is the weather tomorrow?",
            user_context={"province": "Ontario"},
        )
    )

    assert "Ontario healthcare navigation" in response.answer
    assert response.citations == []
    assert response.metadata["implementation_status"] == "deterministic_agent_safety"
    assert response.metadata["safety_route"] == "out_of_scope"
