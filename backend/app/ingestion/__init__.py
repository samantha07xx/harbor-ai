"""Source ingestion modules."""

from app.ingestion.crawler import (
    Crawler,
    PageFetchError,
    UrlAllowlistDecision,
    UrlNotAllowedError,
    find_allowed_source,
)
from app.ingestion.extractor import extract_page
from app.ingestion.page_ingestion import PageIngestionResult, PageIngestionService
from app.ingestion.source_registry import get_enabled_sources, load_trusted_sources

__all__ = [
    "Crawler",
    "PageFetchError",
    "PageIngestionResult",
    "PageIngestionService",
    "UrlAllowlistDecision",
    "UrlNotAllowedError",
    "extract_page",
    "find_allowed_source",
    "get_enabled_sources",
    "load_trusted_sources",
]
