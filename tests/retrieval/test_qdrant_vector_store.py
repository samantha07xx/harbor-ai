import httpx
import pytest

from app.retrieval.qdrant_client import (
    InMemoryVectorStore,
    QdrantPoint,
    QdrantVectorStore,
    cosine_similarity,
    extract_collection_vector_size,
)


def make_point(point_id: str, vector: list[float], text: str) -> QdrantPoint:
    return QdrantPoint(
        id=point_id,
        vector=vector,
        payload={
            "chunk_id": point_id,
            "text": text,
            "source_id": "ontario_health_pages",
        },
    )


def test_cosine_similarity_scores_matching_vectors_highest() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_in_memory_vector_store_upserts_and_searches_points() -> None:
    store = InMemoryVectorStore()
    store.upsert_points(
        [
            make_point("point_a", [1.0, 0.0], "OHIP application"),
            make_point("point_b", [0.0, 1.0], "Health811"),
        ]
    )

    hits = store.search([1.0, 0.0], limit=1)

    assert len(hits) == 1
    assert hits[0].id == "point_a"
    assert hits[0].payload["text"] == "OHIP application"


def test_in_memory_vector_store_replaces_existing_point() -> None:
    store = InMemoryVectorStore()
    store.upsert_points([make_point("point_a", [1.0, 0.0], "Old text")])
    store.upsert_points([make_point("point_a", [1.0, 0.0], "New text")])

    hits = store.search([1.0, 0.0], limit=1)

    assert hits[0].payload["text"] == "New text"


def test_qdrant_vector_store_upserts_points_with_expected_request() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json={"result": {"operation_id": 1}}, request=request)

    store = QdrantVectorStore(
        url="http://qdrant.test",
        collection_name="harbor_healthcare_chunks",
        api_key="test-key",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    store.upsert_points([make_point("point_a", [0.1, 0.2], "OHIP")])

    assert captured_request is not None
    assert captured_request.method == "PUT"
    assert captured_request.url.path == "/collections/harbor_healthcare_chunks/points"
    assert captured_request.headers["api-key"] == "test-key"
    assert b'"id":"point_a"' in captured_request.content


def test_qdrant_vector_store_ensure_collection_creates_missing_collection() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        if request.method == "GET":
            return httpx.Response(404, request=request)
        return httpx.Response(200, json={"result": True}, request=request)

    store = QdrantVectorStore(
        url="http://qdrant.test",
        collection_name="harbor_healthcare_chunks",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    store.ensure_collection(vector_size=4)

    assert [request.method for request in captured_requests] == ["GET", "PUT"]
    assert captured_requests[1].url.path == "/collections/harbor_healthcare_chunks"
    assert b'"size":4' in captured_requests[1].content
    assert b'"distance":"Cosine"' in captured_requests[1].content


def test_qdrant_vector_store_ensure_collection_accepts_matching_collection() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(
            200,
            json={
                "result": {
                    "config": {
                        "params": {
                            "vectors": {
                                "size": 4,
                                "distance": "Cosine",
                            }
                        }
                    }
                }
            },
            request=request,
        )

    store = QdrantVectorStore(
        url="http://qdrant.test",
        collection_name="harbor_healthcare_chunks",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    store.ensure_collection(vector_size=4)

    assert [request.method for request in captured_requests] == ["GET"]


def test_qdrant_vector_store_ensure_collection_rejects_vector_size_mismatch() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "result": {
                    "config": {
                        "params": {
                            "vectors": {
                                "size": 16,
                                "distance": "Cosine",
                            }
                        }
                    }
                }
            },
            request=request,
        )

    store = QdrantVectorStore(
        url="http://qdrant.test",
        collection_name="harbor_healthcare_chunks",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(ValueError, match="does not match"):
        store.ensure_collection(vector_size=4)


def test_qdrant_vector_store_search_maps_results() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/collections/harbor_healthcare_chunks/points/search"
        assert b'"with_payload":true' in request.content
        return httpx.Response(
            200,
            json={
                "result": [
                    {
                        "id": "point_a",
                        "score": 0.88,
                        "payload": {"text": "OHIP application"},
                    }
                ]
            },
            request=request,
        )

    store = QdrantVectorStore(
        url="http://qdrant.test",
        collection_name="harbor_healthcare_chunks",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    hits = store.search([0.1, 0.2], limit=1)

    assert len(hits) == 1
    assert hits[0].id == "point_a"
    assert hits[0].score == 0.88
    assert hits[0].payload["text"] == "OHIP application"


def test_qdrant_vector_store_rejects_empty_search_vector() -> None:
    store = QdrantVectorStore(
        url="http://qdrant.test",
        collection_name="harbor_healthcare_chunks",
        http_client=httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200))),
    )

    with pytest.raises(ValueError, match="cannot be empty"):
        store.search([])


def test_extract_collection_vector_size_returns_none_for_missing_metadata() -> None:
    assert extract_collection_vector_size({"result": {}}) is None
