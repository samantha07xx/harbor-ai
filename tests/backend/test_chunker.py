from datetime import UTC, datetime

from app.ingestion.chunker import (
    CHUNKING_VERSION,
    ChunkingSettings,
    chunk_extracted_page,
    estimate_token_count,
    hash_chunk_text,
)
from app.schemas.sources import ExtractedPage, TrustTier


def make_extracted_page(clean_text: str, headings: list[str] | None = None) -> ExtractedPage:
    return ExtractedPage(
        source_id="ontario_health_pages",
        url="https://www.ontario.ca/page/apply-ohip-and-get-health-card",
        canonical_url="https://www.ontario.ca/page/apply-ohip-and-get-health-card",
        title="Apply for OHIP and get a health card",
        clean_text=clean_text,
        clean_text_hash=hash_chunk_text(clean_text),
        headings=headings or ["Apply for OHIP and get a health card"],
        links=[],
        extracted_at=datetime.now(UTC),
        trust_tier=TrustTier.OFFICIAL_GOVERNMENT,
    )


def test_estimate_token_count_returns_positive_count() -> None:
    assert estimate_token_count("Apply for OHIP.") == 4
    assert estimate_token_count("") == 1


def test_chunk_extracted_page_preserves_metadata() -> None:
    page = make_extracted_page(
        (
            "Apply for OHIP and get a health card\n"
            "Who qualifies\n"
            "You need to make Ontario your primary residence."
        ),
        headings=["Apply for OHIP and get a health card", "Who qualifies"],
    )

    chunks = chunk_extracted_page(page)

    assert len(chunks) == 1
    assert chunks[0].source_id == "ontario_health_pages"
    assert str(chunks[0].source_url) == "https://www.ontario.ca/page/apply-ohip-and-get-health-card"
    assert chunks[0].section_heading == "Apply for OHIP and get a health card"
    assert chunks[0].topic == "health_card_application"
    assert chunks[0].trust_tier == "official_government"
    assert chunks[0].chunking_version == CHUNKING_VERSION


def test_chunk_extracted_page_splits_long_text_with_overlap() -> None:
    paragraphs = [
        "Apply for OHIP and get a health card",
        "First paragraph about Ontario residency and health coverage.",
        "Second paragraph about documents and ServiceOntario.",
        "Third paragraph about applying in person.",
        "Fourth paragraph about bringing original documents.",
    ]
    page = make_extracted_page("\n".join(paragraphs))

    chunks = chunk_extracted_page(
        page,
        ChunkingSettings(target_token_count=24, overlap_token_count=8),
    )

    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[0].chunk_id.endswith("_0000")
    assert chunks[1].chunk_id.endswith("_0001")
    assert "Second paragraph" in chunks[0].text
    assert "Second paragraph" in chunks[1].text


def test_chunk_extracted_page_infers_required_documents_topic() -> None:
    page = make_extracted_page(
        "Documents needed to get a health card\nBring proof of identity and proof of residency.",
        headings=["Documents needed to get a health card"],
    )

    chunks = chunk_extracted_page(page)

    assert chunks[0].topic == "required_documents"
    assert chunks[0].content_hash.startswith("sha256:")
    assert chunks[0].token_count > 0
