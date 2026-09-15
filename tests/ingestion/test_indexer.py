import httpx

from app.ingestion.chunker import ChunkingSettings
from app.ingestion.crawler import Crawler
from app.ingestion.indexer import DryRunIndexer, IndexingService
from app.ingestion.page_ingestion import PageIngestionService
from app.ingestion.source_registry import get_enabled_sources
from app.retrieval.embeddings import DeterministicEmbeddingProvider, EmbeddingService
from app.retrieval.qdrant_client import InMemoryVectorStore


def make_indexer(handler) -> DryRunIndexer:
    crawler = Crawler(
        get_enabled_sources(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    return DryRunIndexer(
        page_ingestion_service=PageIngestionService(crawler),
        embedding_service=EmbeddingService(DeterministicEmbeddingProvider(dimensions=8)),
    )


def make_indexing_service(handler) -> tuple[IndexingService, InMemoryVectorStore]:
    vector_store = InMemoryVectorStore()
    return IndexingService(make_indexer(handler), vector_store), vector_store


def test_prepare_one_page_returns_chunks_embeddings_and_points() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text="""
            <html>
              <body>
                <main>
                  <h1>Apply for OHIP and get a health card</h1>
                  <p>There is no longer a waiting period for OHIP coverage.</p>
                  <p>You need to make Ontario your primary residence.</p>
                </main>
              </body>
            </html>
            """,
            request=request,
        )

    indexer = make_indexer(handler)

    result = indexer.prepare_one_page(
        "https://www.ontario.ca/page/apply-ohip-and-get-health-card",
        chunking_settings=ChunkingSettings(target_token_count=30, overlap_token_count=5),
    )

    assert result.chunk_count == len(result.page_result.chunks)
    assert result.point_count == len(result.page_result.chunks)
    assert result.point_count == len(result.embeddings)
    assert result.points[0].vector == result.embeddings[0].vector
    assert result.points[0].payload["source_id"] == "ontario_health_pages"
    assert result.points[0].payload["embedding_dimensions"] == 8
    assert "OHIP" in result.points[0].payload["text"]


def test_prepare_one_page_does_not_require_qdrant() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/html"},
            text="<main><h1>Health811</h1><p>Call 811 for non-emergency advice.</p></main>",
            request=request,
        )

    indexer = make_indexer(handler)

    result = indexer.prepare_one_page("https://health811.ontario.ca/")

    assert result.point_count == 1
    assert result.points[0].payload["source_id"] == "health811"
    assert result.points[0].payload["topic"] == "non_emergency_advice"


def test_index_one_page_upserts_points_into_vector_store() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text="""
            <main>
              <h1>Apply for OHIP and get a health card</h1>
              <p>You need to make Ontario your primary residence.</p>
              <p>You need to be physically in Ontario for a required number of days.</p>
            </main>
            """,
            request=request,
        )

    service, vector_store = make_indexing_service(handler)

    result = service.index_one_page(
        "https://www.ontario.ca/page/apply-ohip-and-get-health-card",
        chunking_settings=ChunkingSettings(target_token_count=24, overlap_token_count=5),
    )

    assert result.upserted_point_count == result.dry_run.point_count
    assert len(vector_store.points) == result.upserted_point_count

    query_vector = result.dry_run.points[0].vector
    hits = vector_store.search(query_vector, limit=1)

    assert len(hits) == 1
    assert hits[0].payload["source_id"] == "ontario_health_pages"
    assert "Ontario" in hits[0].payload["text"]
