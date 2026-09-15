from datetime import UTC, datetime

from app.retrieval.embeddings import EmbeddingResult, EmbeddingService
from app.retrieval.qdrant_client import InMemoryVectorStore, map_chunk_to_qdrant_point
from app.retrieval.query_rewrite import QueryIntent, QueryRewriteService
from app.retrieval.service import RetrievalService, RewrittenRetrievalService
from app.schemas.chunks import SourceChunk
from app.schemas.sources import TopicCategory, TrustTier

HASH = "sha256:" + "b" * 64


class KeywordEmbeddingProvider:
    model = "keyword-test-embedding"

    def embed_text(self, text: str) -> EmbeddingResult:
        lower_text = text.lower()
        if "811" in lower_text or "health811" in lower_text:
            vector = [0.0, 1.0, 0.0]
        elif "newcomer" in lower_text:
            vector = [0.0, 0.0, 1.0]
        else:
            vector = [1.0, 0.0, 0.0]
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


def make_service() -> RewrittenRetrievalService:
    store = InMemoryVectorStore()
    chunks = [
        (
            make_chunk(
                chunk_id="chunk_ohip",
                title="Apply for OHIP and get a health card",
                text="Apply for OHIP at ServiceOntario.",
                topic=TopicCategory.HEALTH_CARD_APPLICATION,
            ),
            [1.0, 0.0, 0.0],
        ),
        (
            make_chunk(
                chunk_id="chunk_health811",
                title="Health811",
                text="Call 811 for non-emergency health advice.",
                topic=TopicCategory.NON_EMERGENCY_ADVICE,
            ),
            [0.0, 1.0, 0.0],
        ),
        (
            make_chunk(
                chunk_id="chunk_newcomer",
                title="Healthcare options for newcomers",
                text="Newcomers can learn about Ontario health coverage and care options.",
                topic=TopicCategory.NEWCOMER_HEALTH_SERVICES,
            ),
            [0.0, 0.0, 1.0],
        ),
    ]
    store.upsert_points(
        [
            map_chunk_to_qdrant_point(
                chunk,
                EmbeddingResult(
                    text=chunk.text,
                    model="keyword-test-embedding",
                    vector=vector,
                ),
            )
            for chunk, vector in chunks
        ]
    )
    retrieval_service = RetrievalService(
        embedding_service=EmbeddingService(KeywordEmbeddingProvider()),
        vector_store=store,
    )
    return RewrittenRetrievalService(
        query_rewrite_service=QueryRewriteService(),
        retrieval_service=retrieval_service,
    )


def test_rewritten_retrieval_uses_primary_rewritten_query() -> None:
    service = make_service()

    result = service.retrieve("Can I call someone if it is not an emergency?", limit=1)

    assert result.original_question == "Can I call someone if it is not an emergency?"
    assert result.rewrite.detected_intent == QueryIntent.NON_EMERGENCY_ADVICE
    assert result.retrieval.query == "Ontario non-emergency health advice call 811 Health811"
    assert len(result.retrieval.hits) == 1
    assert result.retrieval.hits[0].chunk.chunk_id == "chunk_health811"


def test_rewritten_retrieval_preserves_multi_query_rewrite_metadata() -> None:
    service = make_service()

    result = service.retrieve("I just landed and need a doctor. What can I do?", limit=1)

    assert result.rewrite.detected_intent == QueryIntent.NEWCOMER_HEALTHCARE_ACCESS
    assert len(result.rewrite.rewritten_queries) == 3
    assert result.retrieval.query == result.rewrite.primary_query
    assert result.retrieval.hits[0].chunk.chunk_id == "chunk_newcomer"


def test_rewritten_retrieval_preserves_safety_signal() -> None:
    service = make_service()

    result = service.retrieve("I have chest pain, is this an emergency?", limit=1)

    assert result.rewrite.detected_intent == QueryIntent.EMERGENCY
    assert result.rewrite.needs_safety_check is True
