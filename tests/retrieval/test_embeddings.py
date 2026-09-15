from datetime import UTC, datetime

import pytest

from app.retrieval.embeddings import (
    DeterministicEmbeddingProvider,
    EmbeddingService,
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


def test_embedding_service_embeds_query_and_chunk() -> None:
    provider = DeterministicEmbeddingProvider(dimensions=6)
    service = EmbeddingService(provider)

    query_result = service.embed_query("Ontario apply for OHIP")
    chunk_result = service.embed_chunk(make_chunk())

    assert query_result.dimensions == 6
    assert chunk_result.dimensions == 6
    assert chunk_result.text.startswith("Title: Apply for OHIP")
