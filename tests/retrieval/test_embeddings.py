from datetime import UTC, datetime

import httpx
import pytest

from app.config import get_settings
from app.retrieval.embeddings import (
    DeterministicEmbeddingProvider,
    EmbeddingService,
    LocalKeywordEmbeddingProvider,
    OpenAIEmbeddingProvider,
    build_configured_embedding_service,
    format_chunk_for_embedding,
)
from app.schemas.chunks import SourceChunk
from app.schemas.sources import TopicCategory, TrustTier

HASH = "sha256:" + "a" * 64


def make_chunk() -> SourceChunk:
    return SourceChunk(
        chunk_id="chunk_ontario_ohip_0001",
        page_id="page_ontario_ohip",
        source_id="ontario_health_pages",
        source_url="https://www.ontario.ca/page/apply-ohip-and-get-health-card",
        title="Apply for OHIP and get a health card",
        section_heading="Who qualifies",
        topic=TopicCategory.OHIP_ELIGIBILITY,
        trust_tier=TrustTier.OFFICIAL_GOVERNMENT,
        chunk_index=1,
        text="You need to make Ontario your primary residence.",
        token_count=9,
        content_hash=HASH,
        last_crawled_at=datetime.now(UTC),
    )


def test_format_chunk_for_embedding_matches_design_baseline() -> None:
    formatted = format_chunk_for_embedding(make_chunk())

    assert "Title: Apply for OHIP and get a health card" in formatted
    assert "Section: Who qualifies" in formatted
    assert "Topic: ohip_eligibility" in formatted
    assert "Content: You need to make Ontario your primary residence." in formatted


def test_deterministic_provider_returns_stable_normalized_vectors() -> None:
    provider = DeterministicEmbeddingProvider(dimensions=8)

    first = provider.embed_text("Ontario health card")
    second = provider.embed_text("Ontario health card")

    assert first.vector == second.vector
    assert first.dimensions == 8
    assert sum(value * value for value in first.vector) == pytest.approx(1.0)


def test_deterministic_provider_rejects_empty_text() -> None:
    provider = DeterministicEmbeddingProvider()

    with pytest.raises(ValueError, match="empty text"):
        provider.embed_text("   ")


def test_local_keyword_provider_maps_health_card_text() -> None:
    provider = LocalKeywordEmbeddingProvider()

    result = provider.embed_text("How do I apply for a health card?")

    assert result.model == "local-keyword-fixture"
    assert result.vector == [1.0, 0.0, 0.0, 0.0]


def test_openai_embedding_provider_posts_to_embeddings_api() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "embedding": [0.1, 0.2, 0.3],
                    }
                ]
            },
            request=request,
        )

    provider = OpenAIEmbeddingProvider(
        api_key="test-key",
        model="text-embedding-3-small",
        base_url="https://api.openai.test/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = provider.embed_text("Ontario health card")

    assert captured_request is not None
    assert captured_request.url.path == "/v1/embeddings"
    assert captured_request.headers["authorization"] == "Bearer test-key"
    assert b'"model":"text-embedding-3-small"' in captured_request.content
    assert result.model == "text-embedding-3-small"
    assert result.vector == [0.1, 0.2, 0.3]


def test_openai_embedding_provider_requires_api_key() -> None:
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAIEmbeddingProvider(api_key="")


def test_build_configured_embedding_service_supports_openai(monkeypatch) -> None:
    monkeypatch.setenv("HARBOR_EMBEDDING_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("HARBOR_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    get_settings.cache_clear()

    service = build_configured_embedding_service()

    assert isinstance(service.provider, OpenAIEmbeddingProvider)
    assert service.provider.model == "text-embedding-3-small"
    get_settings.cache_clear()


def test_embedding_service_embeds_query_and_chunk() -> None:
    provider = DeterministicEmbeddingProvider(dimensions=6)
    service = EmbeddingService(provider)

    query_result = service.embed_query("Ontario apply for OHIP")
    chunk_result = service.embed_chunk(make_chunk())

    assert query_result.dimensions == 6
    assert chunk_result.dimensions == 6
    assert chunk_result.text.startswith("Title: Apply for OHIP")
