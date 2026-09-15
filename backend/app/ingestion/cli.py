"""Command-line helpers for local ingestion dry runs and Qdrant indexing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import httpx

from app.ingestion.chunker import ChunkingSettings
from app.ingestion.crawler import Crawler
from app.ingestion.indexer import DryRunIndexer, DryRunIndexingResult, IndexingService
from app.ingestion.page_ingestion import PageIngestionService
from app.ingestion.source_registry import get_enabled_sources
from app.retrieval.embeddings import (
    DeterministicEmbeddingProvider,
    EmbeddingService,
    build_configured_embedding_service,
)
from app.retrieval.live import DEFAULT_LIVE_INGESTION_URLS
from app.retrieval.qdrant_client import QdrantVectorStore, VectorStore

DEFAULT_URL = "https://www.ontario.ca/page/apply-ohip-and-get-health-card"


def build_dry_run_indexer(
    *,
    embedding_dimensions: int = 16,
    fixture_html_path: Path | None = None,
) -> DryRunIndexer:
    """Build a dry-run indexer for CLI usage."""

    http_client = None
    if fixture_html_path is not None:
        fixture_html = fixture_html_path.read_text(encoding="utf-8")
        http_client = httpx.Client(transport=httpx.MockTransport(make_fixture_handler(fixture_html)))

    crawler = Crawler(
        get_enabled_sources(),
        http_client=http_client,
    )
    return DryRunIndexer(
        page_ingestion_service=PageIngestionService(crawler),
        embedding_service=EmbeddingService(
            DeterministicEmbeddingProvider(dimensions=embedding_dimensions),
        ),
    )


def build_qdrant_indexing_service(
    *,
    fixture_html_path: Path | None = None,
    vector_store: VectorStore | None = None,
) -> tuple[IndexingService, EmbeddingService, VectorStore]:
    """Build the live-page indexing service used for Qdrant writes."""

    http_client = None
    if fixture_html_path is not None:
        fixture_html = fixture_html_path.read_text(encoding="utf-8")
        http_client = httpx.Client(transport=httpx.MockTransport(make_fixture_handler(fixture_html)))

    crawler = Crawler(
        get_enabled_sources(),
        http_client=http_client,
    )
    embedding_service = build_configured_embedding_service(default_provider="local_keyword")
    configured_vector_store = vector_store or QdrantVectorStore()
    return (
        IndexingService(
            dry_run_indexer=DryRunIndexer(
                page_ingestion_service=PageIngestionService(crawler),
                embedding_service=embedding_service,
            ),
            vector_store=configured_vector_store,
        ),
        embedding_service,
        configured_vector_store,
    )


def make_fixture_handler(fixture_html: str):
    """Create an httpx mock handler for fixture-backed dry runs."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text=fixture_html,
            request=request,
        )

    return handler


def summarize_dry_run(result: DryRunIndexingResult) -> dict[str, Any]:
    """Create a compact JSON-serializable dry-run summary."""

    first_chunk = result.page_result.chunks[0] if result.page_result.chunks else None
    return {
        "url": str(result.page_result.fetched_page.url),
        "source_id": result.page_result.fetched_page.source_id,
        "title": result.page_result.extracted_page.title,
        "chunk_count": result.chunk_count,
        "embedding_count": len(result.embeddings),
        "point_count": result.point_count,
        "first_chunk_preview": first_chunk.text[:160] if first_chunk else None,
        "first_point_id": result.points[0].id if result.points else None,
        "first_point_payload_keys": sorted(result.points[0].payload.keys()) if result.points else [],
    }


def run_dry_run(
    *,
    url: str = DEFAULT_URL,
    fixture_html_path: Path | None = None,
    target_token_count: int = 120,
    overlap_token_count: int = 20,
    embedding_dimensions: int = 16,
) -> dict[str, Any]:
    """Run the local fetch/extract/chunk/embed/index dry-run preview."""

    indexer = build_dry_run_indexer(
        embedding_dimensions=embedding_dimensions,
        fixture_html_path=fixture_html_path,
    )
    result = indexer.prepare_one_page(
        url,
        chunking_settings=ChunkingSettings(
            target_token_count=target_token_count,
            overlap_token_count=overlap_token_count,
        ),
    )
    return summarize_dry_run(result)


def run_qdrant_index(
    *,
    urls: list[str],
    fixture_html_path: Path | None = None,
    target_token_count: int = 220,
    overlap_token_count: int = 40,
    ensure_collection: bool = True,
    vector_store: VectorStore | None = None,
) -> dict[str, Any]:
    """Fetch allowlisted pages, prepare points, and upsert them into Qdrant."""

    indexing_service, embedding_service, configured_vector_store = build_qdrant_indexing_service(
        fixture_html_path=fixture_html_path,
        vector_store=vector_store,
    )
    embedding_dimensions = embedding_service.embed_query("Ontario healthcare navigation").dimensions

    if ensure_collection and isinstance(configured_vector_store, QdrantVectorStore):
        configured_vector_store.ensure_collection(vector_size=embedding_dimensions)

    indexed_pages: list[dict[str, Any]] = []
    failed_pages: list[dict[str, str]] = []
    upserted_point_count = 0

    for url in urls:
        try:
            result = indexing_service.index_one_page(
                url,
                chunking_settings=ChunkingSettings(
                    target_token_count=target_token_count,
                    overlap_token_count=overlap_token_count,
                ),
            )
        except (ValueError, httpx.HTTPError) as error:
            failed_pages.append({"url": url, "error": str(error)})
            continue

        upserted_point_count += result.upserted_point_count
        indexed_pages.append(
            {
                "url": str(result.dry_run.page_result.fetched_page.url),
                "source_id": result.dry_run.page_result.fetched_page.source_id,
                "title": result.dry_run.page_result.extracted_page.title,
                "chunk_count": result.dry_run.chunk_count,
                "upserted_point_count": result.upserted_point_count,
            }
        )

    return {
        "retrieval_mode": "qdrant",
        "collection": getattr(configured_vector_store, "collection_name", None),
        "embedding_model": embedding_service.provider.model,
        "embedding_dimensions": embedding_dimensions,
        "requested_url_count": len(urls),
        "indexed_page_count": len(indexed_pages),
        "upserted_point_count": upserted_point_count,
        "indexed_pages": indexed_pages,
        "failed_pages": failed_pages,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(description="Run Harbor ingestion previews or Qdrant indexing.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Approved source URL to dry-run.")
    parser.add_argument(
        "--default-live-urls",
        action="store_true",
        help="Index the current default allowlisted live retrieval URLs.",
    )
    parser.add_argument(
        "--fixture-html",
        type=Path,
        default=None,
        help="Optional local HTML file used instead of a network fetch.",
    )
    parser.add_argument("--target-token-count", type=int, default=120)
    parser.add_argument("--overlap-token-count", type=int, default=20)
    parser.add_argument("--embedding-dimensions", type=int, default=16)
    parser.add_argument(
        "--write-to-qdrant",
        action="store_true",
        help="Write prepared points into the configured Qdrant collection.",
    )
    parser.add_argument(
        "--skip-ensure-collection",
        action="store_true",
        help="Do not create or validate the Qdrant collection before indexing.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the ingestion CLI."""

    args = build_parser().parse_args(argv)
    if args.write_to_qdrant:
        urls = DEFAULT_LIVE_INGESTION_URLS if args.default_live_urls else [args.url]
        summary = run_qdrant_index(
            urls=urls,
            fixture_html_path=args.fixture_html,
            target_token_count=args.target_token_count,
            overlap_token_count=args.overlap_token_count,
            ensure_collection=not args.skip_ensure_collection,
        )
    else:
        summary = run_dry_run(
            url=args.url,
            fixture_html_path=args.fixture_html,
            target_token_count=args.target_token_count,
            overlap_token_count=args.overlap_token_count,
            embedding_dimensions=args.embedding_dimensions,
        )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
