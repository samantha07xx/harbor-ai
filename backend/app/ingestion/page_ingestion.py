"""Single-page ingestion service.

This step composes guarded fetching with HTML extraction for one approved page.
It does not recursively crawl links, chunk text, embed content, or index data.
"""

from dataclasses import dataclass

from app.ingestion.crawler import Crawler
from app.ingestion.extractor import extract_page
from app.schemas.sources import ExtractedPage, FetchedPage


@dataclass(frozen=True)
class PageIngestionResult:
    """Fetched and extracted representation of one approved page."""

    fetched_page: FetchedPage
    extracted_page: ExtractedPage


class PageIngestionService:
    """Orchestrates one-page fetch and extraction."""

    def __init__(self, crawler: Crawler) -> None:
        self.crawler = crawler

    def ingest_one_page(self, url: str) -> PageIngestionResult:
        """Fetch and extract one allowlisted page."""

        fetched_page = self.crawler.fetch_page(url)
        extracted_page = extract_page(fetched_page)
        return PageIngestionResult(
            fetched_page=fetched_page,
            extracted_page=extracted_page,
        )
