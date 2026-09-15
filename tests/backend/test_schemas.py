from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.chunks import RetrievalHit, SourceChunk
from app.schemas.sources import SourcePage, TopicCategory, TrustedSource, TrustTier

HASH = "sha256:" + "a" * 64


def test_trusted_source_matches_design_baseline() -> None:
    source = TrustedSource(
        source_id="ontario_ohip",
        name="Ontario.ca OHIP",
        base_url="https://www.ontario.ca/",
        seed_urls=["https://www.ontario.ca/page/apply-ohip-and-get-health-card"],
        allowed_url_patterns=["https://www.ontario.ca/page/*ohip*"],
        trust_tier=TrustTier.OFFICIAL_GOVERNMENT,
    )

    assert source.enabled is True
    assert source.jurisdiction == "Ontario"
    assert source.language == "en"


def test_source_page_validates_hash_format() -> None:
    with pytest.raises(ValidationError):
        SourcePage(
            page_id="page_abc123",
            source_id="ontario_ohip",
            url="https://www.ontario.ca/page/apply-ohip-and-get-health-card",
            title="Apply for OHIP and get a health card",
            clean_text_hash="not-a-sha256-hash",
            last_crawled_at=datetime.now(UTC),
            http_status=200,
            trust_tier=TrustTier.OFFICIAL_GOVERNMENT,
        )


def test_source_chunk_can_create_citation() -> None:
    chunk = SourceChunk(
        chunk_id="chunk_abc123_0004",
        page_id="page_abc123",
        source_id="ontario_ohip",
        source_url="https://www.ontario.ca/page/apply-ohip-and-get-health-card",
        title="Apply for OHIP and get a health card",
        section_heading="How to apply",
        topic=TopicCategory.HEALTH_CARD_APPLICATION,
        trust_tier=TrustTier.OFFICIAL_GOVERNMENT,
        chunk_index=4,
        text="Cleaned chunk text.",
        token_count=734,
        content_hash=HASH,
        last_crawled_at=datetime.now(UTC),
    )

    hit = RetrievalHit(chunk=chunk, score=0.78)
    citation = hit.to_citation()

    assert citation.title == "Apply for OHIP and get a health card"
    assert str(citation.url) == "https://www.ontario.ca/page/apply-ohip-and-get-health-card"
    assert citation.section_heading == "How to apply"


def test_retrieval_score_must_be_normalized() -> None:
    chunk = SourceChunk(
        chunk_id="chunk_abc123_0004",
        page_id="page_abc123",
        source_id="ontario_ohip",
        source_url="https://www.ontario.ca/page/apply-ohip-and-get-health-card",
        title="Apply for OHIP and get a health card",
        trust_tier=TrustTier.OFFICIAL_GOVERNMENT,
        chunk_index=4,
        text="Cleaned chunk text.",
        token_count=734,
        content_hash=HASH,
        last_crawled_at=datetime.now(UTC),
    )

    with pytest.raises(ValidationError):
        RetrievalHit(chunk=chunk, score=1.5)
