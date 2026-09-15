from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_placeholder() -> None:
    response = client.post(
        "/api/chat",
        json={
            "session_id": "test-session",
            "message": "How do I apply for OHIP?",
            "user_context": {"province": "Ontario"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["implementation_status"] == "backend_scaffold_only"
    assert body["citations"] == []
