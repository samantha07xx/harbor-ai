from fastapi.testclient import TestClient

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
    assert body["metadata"]["implementation_status"] == "pre_agent_local_rag"
    assert body["metadata"]["detected_intent"] == "non_emergency_advice"
    assert body["metadata"]["retrieval_hit_count"] == 1
