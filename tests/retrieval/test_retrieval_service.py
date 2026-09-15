from datetime import UTC, datetime

from app.retrieval.embeddings import (
    DeterministicEmbeddingProvider,
    EmbeddingResult,
    EmbeddingService,
)
from app.retrieval.qdrant_client import (
    InMemoryVectorStore,
    QdrantSearchHit,
    map_chunk_to_qdrant_point,
)
from app.retrieval.service import RetrievalService, map_search_hit_to_retrieval_hit
from app.schemas.chunks import SourceChunk
from app.schemas.sources import TopicCategory, TrustTier

HASH = "sha256:" + "a" * 64


class KeywordEmbeddingProvider:
    model = "keyword-test-embedding"

    def embed_text(self, text: str) -> EmbeddingResult:
        lower_text = text.lower()
        if "811" in lower_text or "health811" in lower_text:
            vector = [0.0, 1.0]
        else:
            vector = [1.0, 0.0]
        return EmbeddingResult(text=text, model=self.model, vector=vector)


def make_chunk(
    *,
    chunk_id: str,
    title: str,
    text: str,
    topic: TopicCategory,
) -> SourceChunk:
    return SourceChunk(
        chunk_id=chunk_id,
        page_id=f"page_{chunk_id}",
        source_id="ontario_health_pages",
        source_url="https://www.ontario.ca/page/apply-ohip-and-get-health-card",
        title=title,
        section_heading=title,
        topic=topic,
        trust_tier=TrustTier.OFFICIAL_GOVERNMENT,
        chunk_index=0,
        text=text,
        token_count=10,
        content_hash=HASH,
        last_crawled_at=datetime(2026, 9, 15, tzinfo=UTC),
        embedding_model="keyword-test-embedding",
        chunking_version="heading-paragraph-v1",
    )


def test_map_search_hit_to_retrieval_hit_rebuilds_source_chunk() -> None:
    chunk = make_chunk(
        chunk_id="chunk_ohip",
        title="Apply for OHIP and get a health card",
        text="Apply for OHIP.",
        topic=TopicCategory.HEALTH_CARD_APPLICATION,
    )
    point = map_chunk_to_qdrant_point(
        chunk,
        EmbeddingResult(text="formatted", model="keyword-test-embedding", vector=[1.0, 0.0]),
    )

    retrieval_hit = map_search_hit_to_retrieval_hit(
        QdrantSearchHit(id=point.id, score=0.92, payload=point.payload)
    )

    assert retrieval_hit.score == 0.92
    assert retrieval_hit.chunk.chunk_id == "chunk_ohip"
    assert retrieval_hit.chunk.topic == "health_card_application"
    assert retrieval_hit.to_citation().title == "Apply for OHIP and get a health card"


def test_retrieval_service_embeds_query_and_returns_ranked_results() -> None:
    store = InMemoryVectorStore()
    ohip_chunk = make_chunk(
        chunk_id="chunk_ohip",
        title="Apply for OHIP and get a health card",
        text="Apply for OHIP at ServiceOntario.",
        topic=TopicCategory.HEALTH_CARD_APPLICATION,
    )
    health811_chunk = make_chunk(
        chunk_id="chunk_health811",
        title="Health811",
        text="Call 811 for non-emergency health advice.",
        topic=TopicCategory.NON_EMERGENCY_ADVICE,
    )
    store.upsert_points(
        [
            map_chunk_to_qdrant_point(
                ohip_chunk,
                EmbeddingResult(text="ohip", model="keyword-test-embedding", vector=[1.0, 0.0]),
            ),
            map_chunk_to_qdrant_point(
                health811_chunk,
                EmbeddingResult(text="811", model="keyword-test-embedding", vector=[0.0, 1.0]),
            ),
        ]
    )
    service = RetrievalService(
        embedding_service=EmbeddingService(KeywordEmbeddingProvider()),
        vector_store=store,
    )

    result = service.retrieve("Can I call 811?", limit=1)

    assert result.query == "Can I call 811?"
    assert result.filters == {"jurisdiction": "Ontario", "language": "en"}
    assert len(result.hits) == 1
    assert result.hits[0].chunk.chunk_id == "chunk_health811"
    assert result.hits[0].chunk.topic == "non_emergency_advice"


def test_retrieval_service_returns_empty_result_when_store_has_no_hits() -> None:
    service = RetrievalService(
        embedding_service=EmbeddingService(DeterministicEmbeddingProvider(dimensions=2)),
        vector_store=InMemoryVectorStore(),
    )

    result = service.retrieve("How do I apply for OHIP?")

    assert result.hits == []
