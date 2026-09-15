from datetime import UTC, datetime

import pytest

from app.retrieval.embeddings import EmbeddingResult
from app.retrieval.qdrant_client import (
    make_qdrant_point_id,
    map_chunk_to_qdrant_point,
    map_chunks_to_qdrant_points,
)
from app.schemas.chunks import SourceChunk
from app.schemas.sources import TopicCategory, TrustTier

HASH = "sha256:" + "a" * 64


def make_chunk() -> SourceChunk:
    return SourceChunk(
        chunk_id="chunk_ontario_health_pages_0001",
        page_id="page_ontario_health_pages",
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
        last_crawled_at=datetime(2026, 9, 15, tzinfo=UTC),
        chunking_version="heading-paragraph-v1",
    )


def make_embedding() -> EmbeddingResult:
    return EmbeddingResult(
        text="Title: Apply for OHIP",
        model="deterministic-test-embedding",
        vector=[0.1, 0.2, 0.3],
    )


def test_make_qdrant_point_id_is_stable_hash() -> None:
    point_id = make_qdrant_point_id("chunk_ontario_health_pages_0001")

    assert point_id == make_qdrant_point_id("chunk_ontario_health_pages_0001")
    assert len(point_id) == 64


def test_map_chunk_to_qdrant_point_preserves_vector_and_payload() -> None:
    point = map_chunk_to_qdrant_point(make_chunk(), make_embedding())

    assert point.vector == [0.1, 0.2, 0.3]
    assert point.payload["chunk_id"] == "chunk_ontario_health_pages_0001"
    assert point.payload["source_domain"] == "www.ontario.ca"
    assert point.payload["source_url"] == "https://www.ontario.ca/page/apply-ohip-and-get-health-card"
    assert point.payload["topic"] == "ohip_eligibility"
    assert point.payload["trust_tier"] == "official_government"
    assert point.payload["jurisdiction"] == "Ontario"
    assert point.payload["language"] == "en"
    assert point.payload["embedding_model"] == "deterministic-test-embedding"
    assert point.payload["embedding_dimensions"] == 3
    assert point.payload["last_crawled_at"] == "2026-09-15T00:00:00+00:00"


def test_map_chunk_to_qdrant_point_rejects_empty_vector() -> None:
    empty_embedding = EmbeddingResult(
        text="Title: Apply for OHIP",
        model="deterministic-test-embedding",
        vector=[],
    )

    with pytest.raises(ValueError, match="cannot be empty"):
        map_chunk_to_qdrant_point(make_chunk(), empty_embedding)


def test_map_chunks_to_qdrant_points_maps_all_pairs() -> None:
    points = map_chunks_to_qdrant_points([(make_chunk(), make_embedding())])

    assert len(points) == 1
    assert points[0].payload["page_id"] == "page_ontario_health_pages"
