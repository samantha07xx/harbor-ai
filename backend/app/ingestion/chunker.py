"""Metadata-aware chunking for extracted pages.

Step 11 creates source chunks from one extracted page. It does not generate
embeddings or index anything into Qdrant.
"""

from dataclasses import dataclass
from hashlib import sha256
from re import findall
from urllib.parse import urlparse

from app.schemas.chunks import SourceChunk
from app.schemas.sources import ExtractedPage, TopicCategory

CHUNKING_VERSION = "heading-paragraph-v1"
DEFAULT_TARGET_TOKEN_COUNT = 750
DEFAULT_OVERLAP_TOKEN_COUNT = 100


@dataclass(frozen=True)
class ChunkingSettings:
    """Configurable chunking settings."""

    target_token_count: int = DEFAULT_TARGET_TOKEN_COUNT
    overlap_token_count: int = DEFAULT_OVERLAP_TOKEN_COUNT


def estimate_token_count(text: str) -> int:
    """Estimate token count without requiring tokenizer dependencies."""

    return max(1, len(findall(r"\w+|[^\w\s]", text)))


def hash_chunk_text(text: str) -> str:
    """Return a stable SHA-256 hash for chunk text."""

    return f"sha256:{sha256(text.encode('utf-8')).hexdigest()}"


def make_page_id(page: ExtractedPage) -> str:
    """Create a stable page ID from source and canonical URL."""

    url = str(page.canonical_url or page.url)
    digest = sha256(url.encode("utf-8")).hexdigest()[:16]
    return f"page_{page.source_id}_{digest}"


def infer_topic(page: ExtractedPage, text: str) -> TopicCategory:
    """Infer a broad topic from page metadata and text."""

    haystack = f"{page.title}\n{text}\n{page.url}".lower()

    if any(term in haystack for term in ["documents needed", "proof of identity", "proof of residency"]):
        return TopicCategory.REQUIRED_DOCUMENTS
    if any(term in haystack for term in ["apply for ohip", "health card", "serviceontario"]):
        return TopicCategory.HEALTH_CARD_APPLICATION
    if any(term in haystack for term in ["who qualifies", "eligib", "qualifies"]):
        return TopicCategory.OHIP_ELIGIBILITY
    if any(term in haystack for term in ["family doctor", "health care connect"]):
        return TopicCategory.FINDING_FAMILY_DOCTOR
    if "walk-in" in haystack or "walk in" in haystack:
        return TopicCategory.WALK_IN_CLINICS
    if any(term in haystack for term in ["health811", "811", "non-emergency"]):
        return TopicCategory.NON_EMERGENCY_ADVICE
    if "emergency" in haystack:
        return TopicCategory.EMERGENCY_CARE
    if "newcomer" in haystack:
        return TopicCategory.NEWCOMER_HEALTH_SERVICES
    return TopicCategory.GENERAL_HEALTHCARE_NAVIGATION


def chunk_extracted_page(
    page: ExtractedPage,
    settings: ChunkingSettings | None = None,
) -> list[SourceChunk]:
    """Create metadata-rich chunks from an extracted page."""

    chunking_settings = settings or ChunkingSettings()
    paragraphs = split_into_paragraphs(page.clean_text)
    chunk_texts = group_paragraphs(paragraphs, chunking_settings)
    page_id = make_page_id(page)

    return [
        SourceChunk(
            chunk_id=make_chunk_id(page_id, index),
            page_id=page_id,
            source_id=page.source_id,
            source_url=page.canonical_url or page.url,
            title=page.title,
            section_heading=find_section_heading(page, chunk_text),
            topic=infer_topic(page, chunk_text),
            jurisdiction="Ontario",
            language=page.language,
            trust_tier=page.trust_tier,
            chunk_index=index,
            text=chunk_text,
            token_count=estimate_token_count(chunk_text),
            content_hash=hash_chunk_text(chunk_text),
            last_crawled_at=page.extracted_at,
            chunking_version=CHUNKING_VERSION,
        )
        for index, chunk_text in enumerate(chunk_texts)
    ]


def split_into_paragraphs(text: str) -> list[str]:
    """Split extracted text into paragraph-like blocks."""

    return [paragraph.strip() for paragraph in text.splitlines() if paragraph.strip()]


def group_paragraphs(paragraphs: list[str], settings: ChunkingSettings) -> list[str]:
    """Group paragraphs into chunks with light paragraph-level overlap."""

    chunks: list[str] = []
    current_paragraphs: list[str] = []
    current_token_count = 0

    for paragraph in paragraphs:
        paragraph_token_count = estimate_token_count(paragraph)
        would_exceed_target = (
            current_paragraphs
            and current_token_count + paragraph_token_count > settings.target_token_count
        )

        if would_exceed_target:
            chunks.append("\n".join(current_paragraphs))
            current_paragraphs = overlap_paragraphs(current_paragraphs, settings.overlap_token_count)
            current_token_count = sum(estimate_token_count(item) for item in current_paragraphs)

        current_paragraphs.append(paragraph)
        current_token_count += paragraph_token_count

    if current_paragraphs:
        chunks.append("\n".join(current_paragraphs))

    return chunks


def overlap_paragraphs(paragraphs: list[str], overlap_token_count: int) -> list[str]:
    """Keep trailing paragraphs up to the configured overlap size."""

    if overlap_token_count <= 0:
        return []

    selected: list[str] = []
    token_count = 0

    for paragraph in reversed(paragraphs):
        paragraph_token_count = estimate_token_count(paragraph)
        if selected and token_count + paragraph_token_count > overlap_token_count:
            break
        selected.insert(0, paragraph)
        token_count += paragraph_token_count

    return selected


def make_chunk_id(page_id: str, index: int) -> str:
    """Create a stable chunk ID."""

    return f"chunk_{page_id.removeprefix('page_')}_{index:04d}"


def find_section_heading(page: ExtractedPage, chunk_text: str) -> str | None:
    """Find the first known heading included in a chunk."""

    chunk_lines = {line.strip() for line in chunk_text.splitlines()}
    for heading in page.headings:
        if heading in chunk_lines:
            return heading
    return page.headings[0] if page.headings else None


def source_domain(page: ExtractedPage) -> str:
    """Return the page source domain."""

    return urlparse(str(page.canonical_url or page.url)).hostname or ""
