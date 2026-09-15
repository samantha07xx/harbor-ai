"""Command-line helpers for local ingestion dry runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import httpx

from app.ingestion.chunker import ChunkingSettings
from app.ingestion.crawler import Crawler
from app.ingestion.indexer import DryRunIndexer, DryRunIndexingResult
from app.ingestion.page_ingestion import PageIngestionService
from app.ingestion.source_registry import get_enabled_sources
from app.retrieval.embeddings import DeterministicEmbeddingProvider, EmbeddingService

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


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(description="Run a local Harbor ingestion dry run.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Approved source URL to dry-run.")
    parser.add_argument(
        "--fixture-html",
        type=Path,
        default=None,
        help="Optional local HTML file used instead of a network fetch.",
    )
    parser.add_argument("--target-token-count", type=int, default=120)
    parser.add_argument("--overlap-token-count", type=int, default=20)
    parser.add_argument("--embedding-dimensions", type=int, default=16)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the ingestion dry-run CLI."""

    args = build_parser().parse_args(argv)
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
