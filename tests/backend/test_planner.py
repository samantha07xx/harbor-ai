import httpx
import pytest

from app.agent.planner import (
    AgentPlanRequest,
    AgentPlanRoute,
    OpenAIReActPlanner,
    build_planner_prompt,
    extract_json_object,
    parse_agent_plan,
)


def test_parse_agent_plan_reads_retrieve_route() -> None:
    plan = parse_agent_plan(
        """
        ```json
        {
          "route": "retrieve",
          "message": "",
          "retrieval_question": "Ontario OHIP application health card",
          "rationale": "Needs official source lookup"
        }
        ```
        """
    )

    assert plan.route == AgentPlanRoute.RETRIEVE
    assert plan.retrieval_question == "Ontario OHIP application health card"
    assert plan.rationale == "Needs official source lookup"


def test_parse_agent_plan_reads_direct_answer_route() -> None:
    plan = parse_agent_plan(
        '{"route":"direct_answer","message":"I can help with Ontario healthcare navigation."}'
    )

    assert plan.route == AgentPlanRoute.DIRECT_ANSWER
    assert plan.message == "I can help with Ontario healthcare navigation."
    assert plan.retrieval_question is None


def test_extract_json_object_rejects_missing_json() -> None:
    with pytest.raises(ValueError, match="JSON object"):
        extract_json_object("no json here")


def test_build_planner_prompt_includes_message_and_context() -> None:
    prompt = build_planner_prompt(
        AgentPlanRequest(
            message="How do I apply for OHIP?",
            user_context={"province": "Ontario"},
        )
    )

    assert "How do I apply for OHIP?" in prompt
    assert '"province": "Ontario"' in prompt
    assert "retrieval_question" in prompt


def test_openai_react_planner_posts_responses_request() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "output_text": (
                    '{"route":"retrieve","message":"","retrieval_question":'
                    '"Ontario OHIP application health card","rationale":"Needs source lookup"}'
                )
            },
            request=request,
        )

    planner = OpenAIReActPlanner(
        api_key="test-key",
        model="gpt-5-mini",
        base_url="https://api.openai.test/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    plan = planner.plan(
        AgentPlanRequest(
            message="How do I apply for OHIP?",
            user_context={"province": "Ontario"},
        )
    )

    assert captured_request is not None
    assert captured_request.url.path == "/v1/responses"
    assert captured_request.headers["authorization"] == "Bearer test-key"
    assert b'"max_output_tokens":320' in captured_request.content
    assert b"healthcare_retrieval tool" in captured_request.content
    assert plan.route == AgentPlanRoute.RETRIEVE


def test_openai_react_planner_defaults_to_retrieve_for_malformed_output() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"output_text": ""},
            request=request,
        )

    planner = OpenAIReActPlanner(
        api_key="test-key",
        model="gpt-5-mini",
        base_url="https://api.openai.test/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    plan = planner.plan(
        AgentPlanRequest(
            message="How do I apply for OHIP?",
            user_context={"province": "Ontario"},
        )
    )

    assert plan.route == AgentPlanRoute.RETRIEVE
    assert plan.retrieval_question == "How do I apply for OHIP?"
    assert "not valid JSON" in str(plan.rationale)


def test_openai_react_planner_requires_api_key() -> None:
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAIReActPlanner(api_key="")
