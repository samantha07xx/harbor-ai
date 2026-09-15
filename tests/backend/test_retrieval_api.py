from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_retrieval_search_returns_rewrite_metadata_and_hits() -> None:
    response = client.post(
        "/api/retrieval/search",
        json={
            "question": "Can I call someone if it is not an emergency?",
            "limit": 1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["original_question"] == "Can I call someone if it is not an emergency?"
    assert body["rewrite"]["detected_intent"] == "non_emergency_advice"
    assert body["rewrite"]["primary_query"] == "Ontario non-emergency health advice call 811 Health811"
    assert body["rewrite"]["needs_safety_check"] is False
    assert body["retrieval"]["query"] == body["rewrite"]["primary_query"]
    assert len(body["retrieval"]["hits"]) == 1
    assert body["retrieval"]["hits"][0]["chunk"]["chunk_id"] == "demo_health811"


def test_retrieval_search_preserves_emergency_safety_signal() -> None:
    response = client.post(
        "/api/retrieval/search",
        json={
            "question": "I have chest pain, is this an emergency?",
            "limit": 1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["rewrite"]["detected_intent"] == "emergency"
    assert body["rewrite"]["needs_safety_check"] is True


def test_retrieval_search_rejects_invalid_limit() -> None:
    response = client.post(
        "/api/retrieval/search",
        json={
            "question": "How do I get a health card?",
            "limit": 0,
        },
    )

    assert response.status_code == 422
