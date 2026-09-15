"""Live allowlisted ingestion-backed local retrieval.

This builds an in-memory retrieval index from real allowlisted web pages. It is
still local and deterministic: no external embedding API and no Qdrant writes.
"""

from functools import lru_cache

import httpx

from app.ingestion.chunker import ChunkingSettings
from app.ingestion.crawler import Crawler, CrawlerError
from app.ingestion.indexer import DryRunIndexer
from app.ingestion.page_ingestion import PageIngestionService
from app.ingestion.source_registry import get_enabled_sources
from app.retrieval.demo import get_local_demo_rewritten_retrieval_service
from app.retrieval.embeddings import EmbeddingService, LocalKeywordEmbeddingProvider
from app.retrieval.qdrant_client import InMemoryVectorStore
from app.retrieval.query_rewrite import QueryRewriteService
from app.retrieval.service import RetrievalService, RewrittenRetrievalService

DEFAULT_LIVE_INGESTION_URLS = [
    "https://www.ontario.ca/page/apply-ohip-and-get-health-card",
    "https://www.ontario.ca/page/documents-needed-get-health-card",
    "https://health811.ontario.ca/",
    "https://www.ontario.ca/page/health-care-ontario",
]


class LiveIngestionRetrievalError(RuntimeError):
    """Raised when no live pages can be ingested for retrieval."""


@lru_cache
def get_live_ingested_rewritten_retrieval_service() -> RewrittenRetrievalService:
    """Build and cache a live-ingested in-memory retrieval service."""

    return build_live_ingested_rewritten_retrieval_service(DEFAULT_LIVE_INGESTION_URLS)


def get_live_or_demo_rewritten_retrieval_service() -> RewrittenRetrievalService:
    """Return live-ingested retrieval, falling back to the demo fixture if needed."""

    try:
        return get_live_ingested_rewritten_retrieval_service()
    except LiveIngestionRetrievalError:
        demo_service = get_local_demo_rewritten_retrieval_service()
        demo_service.corpus_mode = "demo_fallback_after_live_ingestion_failure"
        return demo_service


def build_live_ingested_rewritten_retrieval_service(
    urls: list[str],
    *,
    chunking_settings: ChunkingSettings | None = None,
    http_client: httpx.Client | None = None,
) -> RewrittenRetrievalService:
    """Build a local retrieval service by ingesting real allowlisted pages."""

    embedding_service = EmbeddingService(LocalKeywordEmbeddingProvider())
    indexer = DryRunIndexer(
        page_ingestion_service=PageIngestionService(
            Crawler(
                get_enabled_sources(),
                http_client=http_client,
            )
        ),
        embedding_service=embedding_service,
    )
    vector_store = InMemoryVectorStore()
    successful_urls: list[str] = []

    for url in urls:
        try:
            result = indexer.prepare_one_page(
                url,
                chunking_settings=chunking_settings
                or ChunkingSettings(target_token_count=220, overlap_token_count=40),
            )
        except (CrawlerError, ValueError):
            continue

        vector_store.upsert_points(result.points)
        successful_urls.append(url)

    if not vector_store.points:
        raise LiveIngestionRetrievalError("No allowlisted live pages could be ingested")

    service = RewrittenRetrievalService(
        query_rewrite_service=QueryRewriteService(),
        retrieval_service=RetrievalService(
            embedding_service=embedding_service,
            vector_store=vector_store,
        ),
        corpus_mode="live_ingested",
    )
    service.ingested_urls = successful_urls
    return service
