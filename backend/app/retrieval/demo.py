"""Local retrieval fixture for development API testing.

This module avoids Docker and external embedding calls while the API contract is
being developed. It is not the production knowledge base.
"""

from datetime import UTC, datetime
from functools import lru_cache

from app.retrieval.embeddings import EmbeddingResult, EmbeddingService
from app.retrieval.qdrant_client import InMemoryVectorStore, map_chunk_to_qdrant_point
from app.retrieval.query_rewrite import QueryRewriteService
from app.retrieval.service import RetrievalService, RewrittenRetrievalService
from app.schemas.chunks import SourceChunk
from app.schemas.sources import TopicCategory, TrustTier

DEMO_HASH = "sha256:" + "c" * 64


class LocalKeywordEmbeddingProvider:
    """Small deterministic embedding provider for local endpoint testing."""

    model = "local-keyword-fixture"

    def embed_text(self, text: str) -> EmbeddingResult:
        """Map known Harbor MVP topics onto stable fixture vectors."""

        lower_text = text.lower()
        if "newcomer" in lower_text or "new to ontario" in lower_text:
            vector = [0.0, 0.0, 1.0, 0.0]
        elif "811" in lower_text or "health811" in lower_text or "non-emergency" in lower_text:
            vector = [0.0, 1.0, 0.0, 0.0]
        elif "911" in lower_text or "chest pain" in lower_text or "emergency" in lower_text:
            vector = [0.0, 0.0, 0.0, 1.0]
        elif "ohip" in lower_text or "health card" in lower_text or "serviceontario" in lower_text:
            vector = [1.0, 0.0, 0.0, 0.0]
        else:
            vector = [0.5, 0.5, 0.5, 0.5]

        return EmbeddingResult(text=text, model=self.model, vector=vector)


@lru_cache
def get_local_demo_rewritten_retrieval_service() -> RewrittenRetrievalService:
    """Build a cached in-memory retrieval service for local API testing."""

    store = InMemoryVectorStore()
    embedding_provider = LocalKeywordEmbeddingProvider()
    embedding_service = EmbeddingService(embedding_provider)
    store.upsert_points(
        [
            map_chunk_to_qdrant_point(chunk, embedding_service.embed_chunk(chunk))
            for chunk in make_demo_chunks()
        ]
    )

    return RewrittenRetrievalService(
        query_rewrite_service=QueryRewriteService(),
        retrieval_service=RetrievalService(
            embedding_service=embedding_service,
            vector_store=store,
        ),
    )


def make_demo_chunks() -> list[SourceChunk]:
    """Return a tiny local source set for endpoint contract tests."""

    return [
        make_demo_chunk(
            chunk_id="demo_ohip_application",
            title="Apply for OHIP and get a health card",
            source_url="https://www.ontario.ca/page/apply-ohip-and-get-health-card",
            text=(
                "Apply for OHIP and get an Ontario health card through "
                "ServiceOntario using required identity, residency, and status documents."
            ),
            topic=TopicCategory.HEALTH_CARD_APPLICATION,
        ),
        make_demo_chunk(
            chunk_id="demo_health811",
            title="Health811",
            source_url="https://health811.ontario.ca/",
            text="Contact Health811 for free, secure, non-emergency health advice in Ontario.",
            topic=TopicCategory.NON_EMERGENCY_ADVICE,
        ),
        make_demo_chunk(
            chunk_id="demo_newcomer_services",
            title="Healthcare options for newcomers",
            source_url="https://www.ontario.ca/page/health-care-ontario",
            text=(
                "Newcomers to Ontario can learn about health coverage, care options, "
                "family doctors, clinics, and how to access non-emergency advice."
            ),
            topic=TopicCategory.NEWCOMER_HEALTH_SERVICES,
        ),
        make_demo_chunk(
            chunk_id="demo_emergency_care",
            title="Emergency care",
            source_url="https://www.ontario.ca/page/get-medical-advice-telehealth-ontario",
            text="For a medical emergency in Ontario, call 911 or go to the nearest emergency department.",
            topic=TopicCategory.EMERGENCY_CARE,
        ),
    ]


def make_demo_chunk(
    *,
    chunk_id: str,
    title: str,
    source_url: str,
    text: str,
    topic: TopicCategory,
) -> SourceChunk:
    """Create one local demo chunk."""

    return SourceChunk(
        chunk_id=chunk_id,
        page_id=f"page_{chunk_id}",
        source_id="local_demo_fixture",
        source_url=source_url,
        title=title,
        section_heading=title,
        topic=topic,
        trust_tier=TrustTier.OFFICIAL_GOVERNMENT,
        chunk_index=0,
        text=text,
        token_count=len(text.split()),
        content_hash=DEMO_HASH,
        last_crawled_at=datetime(2026, 9, 15, tzinfo=UTC),
        embedding_model=LocalKeywordEmbeddingProvider.model,
        chunking_version="local-demo-v1",
    )
