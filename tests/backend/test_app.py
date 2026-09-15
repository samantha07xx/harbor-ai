import httpx
from fastapi.testclient import TestClient

from app.api.dependencies import get_deterministic_healthcare_agent
from app.main import create_app

client = TestClient(create_app())


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_returns_pre_agent_local_rag_response() -> None:
    response = client.post(
        "/api/chat",
        json={
            "session_id": "test-session",
            "message": "Can I call someone if it is not an emergency?",
            "user_context": {"province": "Ontario"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "Health811" in body["answer"]
    assert body["citations"] == [
        {
            "title": "Health811",
            "url": "https://health811.ontario.ca/",
        }
    ]
    assert body["metadata"]["implementation_status"] == "deterministic_agent_local_rag"
    assert body["metadata"]["agent_mode"] == "deterministic_pre_llm"
    assert body["metadata"]["safety_route"] == "proceed"
    assert body["metadata"]["tool_name"] == "healthcare_retrieval"
    assert body["metadata"]["detected_intent"] == "non_emergency_advice"
    assert body["metadata"]["retrieval_hit_count"] == 1


def test_chat_routes_emergency_question_to_safety_response() -> None:
    response = client.post(
        "/api/chat",
        json={
            "session_id": "test-session",
            "message": "I have chest pain and cannot breathe",
            "user_context": {"province": "Ontario"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"].startswith("If this may be a medical emergency")
    assert body["citations"] == []
    assert body["metadata"]["implementation_status"] == "deterministic_agent_safety"
    assert body["metadata"]["agent_mode"] == "deterministic_pre_llm"
    assert body["metadata"]["safety_route"] == "emergency"


def test_chat_routes_out_of_scope_question_to_scope_response() -> None:
    response = client.post(
        "/api/chat",
        json={
            "session_id": "test-session",
            "message": "What is the weather tomorrow?",
            "user_context": {"province": "Ontario"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "Ontario healthcare navigation" in body["answer"]
    assert body["citations"] == []
    assert body["metadata"]["implementation_status"] == "deterministic_agent_safety"
    assert body["metadata"]["agent_mode"] == "deterministic_pre_llm"
    assert body["metadata"]["safety_route"] == "out_of_scope"


def test_chat_returns_readable_message_when_openai_rate_limited() -> None:
    class RateLimitedAgent:
        def run_turn(self, request):
            http_request = httpx.Request("POST", "https://api.openai.com/v1/responses")
            http_response = httpx.Response(429, request=http_request)
            raise httpx.HTTPStatusError(
                "Too Many Requests",
                request=http_request,
                response=http_response,
            )

    client.app.dependency_overrides[get_deterministic_healthcare_agent] = RateLimitedAgent
    try:
        response = client.post(
            "/api/chat",
            json={
                "session_id": "test-session",
                "message": "How do I apply for OHIP?",
                "user_context": {"province": "Ontario"},
            },
        )
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert "rate limiting" in body["answer"]
    assert body["metadata"]["implementation_status"] == "openai_rate_limited"
    assert body["metadata"]["provider_status_code"] == 429
