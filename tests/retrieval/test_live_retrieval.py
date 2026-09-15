import httpx
import pytest

from app.retrieval.live import (
    LiveIngestionRetrievalError,
    build_live_ingested_rewritten_retrieval_service,
)


def test_live_ingested_retrieval_uses_fetched_page_chunks() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text="""
            <main>
              <h1>Apply for OHIP and get a health card</h1>
              <p>Apply for OHIP through ServiceOntario.</p>
              <p>You need identity, residency, and status documents.</p>
            </main>
            """,
            request=request,
        )

    service = build_live_ingested_rewritten_retrieval_service(
        ["https://www.ontario.ca/page/apply-ohip-and-get-health-card"],
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = service.retrieve("How do I get a health card?", limit=1)

    assert service.corpus_mode == "live_ingested"
    assert result.retrieval.hits[0].chunk.source_id == "ontario_health_pages"
    assert result.retrieval.hits[0].chunk.title == "Apply for OHIP and get a health card"
    assert "ServiceOntario" in result.retrieval.hits[0].chunk.text


def test_live_ingested_retrieval_raises_when_no_page_can_be_ingested() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, request=request)

    with pytest.raises(LiveIngestionRetrievalError):
        build_live_ingested_rewritten_retrieval_service(
            ["https://www.ontario.ca/page/apply-ohip-and-get-health-card"],
            http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        )
