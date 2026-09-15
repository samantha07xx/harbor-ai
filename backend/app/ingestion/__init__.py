"""Source ingestion modules."""

from app.ingestion.chunker import ChunkingSettings, chunk_extracted_page
from app.ingestion.crawler import (
    Crawler,
    PageFetchError,
    UrlAllowlistDecision,
    UrlNotAllowedError,
    find_allowed_source,
)
from app.ingestion.extractor import extract_page
from app.ingestion.indexer import (
    DryRunIndexer,
    DryRunIndexingResult,
    IndexingResult,
    IndexingService,
)
from app.ingestion.page_ingestion import (
    ChunkedPageIngestionResult,
    PageIngestionResult,
    PageIngestionService,
)
from app.ingestion.source_registry import get_enabled_sources, load_trusted_sources

__all__ = [
    "ChunkedPageIngestionResult",
    "ChunkingSettings",
    "Crawler",
    "DryRunIndexer",
    "DryRunIndexingResult",
    "IndexingResult",
    "IndexingService",
    "PageFetchError",
    "PageIngestionResult",
    "PageIngestionService",
    "UrlAllowlistDecision",
    "UrlNotAllowedError",
    "chunk_extracted_page",
    "extract_page",
    "find_allowed_source",
    "get_enabled_sources",
    "load_trusted_sources",
]
