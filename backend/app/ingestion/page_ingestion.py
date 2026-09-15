"""Single-page ingestion service.

This step composes guarded fetching with HTML extraction for one approved page.
It does not recursively crawl links, embed content, or index data.
"""

from dataclasses import dataclass

from app.ingestion.chunker import ChunkingSettings, chunk_extracted_page
from app.ingestion.crawler import Crawler
from app.ingestion.extractor import extract_page
from app.schemas.chunks import SourceChunk
from app.schemas.sources import ExtractedPage, FetchedPage


@dataclass(frozen=True)
class PageIngestionResult:
    """Fetched and extracted representation of one approved page."""

    fetched_page: FetchedPage
    extracted_page: ExtractedPage


@dataclass(frozen=True)
class ChunkedPageIngestionResult:
    """Fetched, extracted, and chunked representation of one approved page."""

    fetched_page: FetchedPage
    extracted_page: ExtractedPage
    chunks: list[SourceChunk]


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

    def ingest_one_page_chunks(
        self,
        url: str,
        *,
        chunking_settings: ChunkingSettings | None = None,
    ) -> ChunkedPageIngestionResult:
        """Fetch, extract, and chunk one allowlisted page."""

        page_result = self.ingest_one_page(url)
        chunks = chunk_extracted_page(
            page_result.extracted_page,
            settings=chunking_settings,
        )
        return ChunkedPageIngestionResult(
            fetched_page=page_result.fetched_page,
            extracted_page=page_result.extracted_page,
            chunks=chunks,
        )
