from app.agent.answer_composer import AnswerComposer
from app.agent.planner import AgentPlan, AgentPlanRequest, AgentPlanRoute
from app.agent.react_agent import AgentTurnRequest, DeterministicHealthcareAgent
from app.agent.tools import HealthcareRetrievalTool
from app.retrieval.demo import get_local_demo_rewritten_retrieval_service
from app.safety.policy import SafetyPolicy


class FakePlanner:
    model = "fake-planner"

    def __init__(self, plan: AgentPlan) -> None:
        self.plan_response = plan
        self.requests: list[AgentPlanRequest] = []

    def plan(self, request: AgentPlanRequest) -> AgentPlan:
        self.requests.append(request)
        return self.plan_response


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


def test_agent_planner_can_answer_directly_without_retrieval() -> None:
    planner = FakePlanner(
        AgentPlan(
            route=AgentPlanRoute.DIRECT_ANSWER,
            message="I can help with Ontario healthcare navigation.",
            rationale="Capability question",
        )
    )
    agent = DeterministicHealthcareAgent(
        safety_policy=SafetyPolicy(),
        retrieval_tool=HealthcareRetrievalTool(
            retrieval_service=get_local_demo_rewritten_retrieval_service(),
            answer_composer=AnswerComposer(),
        ),
        planner=planner,
    )

    response = agent.run_turn(
        AgentTurnRequest(
            session_id="test-session",
            message="What can you help me with?",
            user_context={"province": "Ontario"},
        )
    )

    assert response.answer == "I can help with Ontario healthcare navigation."
    assert response.citations == []
    assert response.metadata["implementation_status"] == "openai_agent_direct_answer"
    assert response.metadata["agent_mode"] == "openai_react_planner"
    assert response.metadata["planner_route"] == "direct_answer"
    assert "tool_name" not in response.metadata
    assert planner.requests[0].message == "What can you help me with?"


def test_agent_planner_retrieval_route_calls_retrieval_tool() -> None:
    planner = FakePlanner(
        AgentPlan(
            route=AgentPlanRoute.RETRIEVE,
            message="",
            retrieval_question="Ontario non-emergency health advice call 811 Health811",
            rationale="Needs official source lookup",
        )
    )
    agent = DeterministicHealthcareAgent(
        safety_policy=SafetyPolicy(),
        retrieval_tool=HealthcareRetrievalTool(
            retrieval_service=get_local_demo_rewritten_retrieval_service(),
            answer_composer=AnswerComposer(),
        ),
        planner=planner,
    )

    response = agent.run_turn(
        AgentTurnRequest(
            session_id="test-session",
            message="Can I call someone if it is not urgent?",
            user_context={"province": "Ontario"},
        )
    )

    assert "Health811" in response.answer
    assert response.metadata["implementation_status"] == "openai_agent_tool_rag"
    assert response.metadata["planner_route"] == "retrieve"
    assert response.metadata["tool_question"] == "Ontario non-emergency health advice call 811 Health811"
    assert response.metadata["tool_name"] == "healthcare_retrieval"
