"""Retrieval services for vector-store-backed healthcare chunks.

Step 18 embeds a query, searches the vector store, and maps hits into
RetrievalResult. Step 20 composes deterministic query rewrite with retrieval,
without calling an agent.
"""

from dataclasses import dataclass
from datetime import datetime

from app.retrieval.embeddings import EmbeddingService
from app.retrieval.qdrant_client import QdrantSearchHit, VectorStore
from app.retrieval.query_rewrite import QueryRewriteResult, QueryRewriteService
from app.schemas.chunks import RetrievalHit, RetrievalResult, SourceChunk


@dataclass(frozen=True)
class RewrittenRetrievalResult:
    """Retrieval result plus the query rewrite metadata that produced it."""

    original_question: str
    rewrite: QueryRewriteResult
    retrieval: RetrievalResult


class RetrievalService:
    """Search indexed healthcare chunks using an embedding service and vector store."""

    def __init__(
        self,
        *,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve(self, query: str, *, limit: int = 6) -> RetrievalResult:
        """Embed a query and return matching source chunks."""

        embedding = self.embedding_service.embed_query(query)
        search_hits = self.vector_store.search(embedding.vector, limit=limit)
        return RetrievalResult(
            query=query,
            hits=[map_search_hit_to_retrieval_hit(hit) for hit in search_hits],
            filters={
                "jurisdiction": "Ontario",
                "language": "en",
            },
        )


class RewrittenRetrievalService:
    """Rewrite a user question before running the retrieval service."""

    def __init__(
        self,
        *,
        query_rewrite_service: QueryRewriteService,
        retrieval_service: RetrievalService,
        corpus_mode: str = "configured",
    ) -> None:
        self.query_rewrite_service = query_rewrite_service
        self.retrieval_service = retrieval_service
        self.corpus_mode = corpus_mode

    def retrieve(self, question: str, *, limit: int = 6) -> RewrittenRetrievalResult:
        """Rewrite a question and retrieve chunks for the primary rewritten query."""

        rewrite = self.query_rewrite_service.rewrite(question)
        retrieval = self.retrieval_service.retrieve(rewrite.primary_query, limit=limit)
        return RewrittenRetrievalResult(
            original_question=question,
            rewrite=rewrite,
            retrieval=retrieval,
        )


def map_search_hit_to_retrieval_hit(hit: QdrantSearchHit) -> RetrievalHit:
    """Map a vector search hit payload into a RetrievalHit."""

    return RetrievalHit(
        chunk=SourceChunk(
            chunk_id=str(hit.payload["chunk_id"]),
            page_id=str(hit.payload["page_id"]),
            source_id=str(hit.payload["source_id"]),
            source_url=str(hit.payload["source_url"]),
            title=str(hit.payload["title"]),
            section_heading=hit.payload.get("section_heading"),
            topic=str(hit.payload["topic"]),
            jurisdiction=str(hit.payload["jurisdiction"]),
            language=str(hit.payload["language"]),
            trust_tier=str(hit.payload["trust_tier"]),
            chunk_index=int(hit.payload["chunk_index"]),
            text=str(hit.payload["text"]),
            token_count=int(hit.payload["token_count"]),
            content_hash=str(hit.payload["content_hash"]),
            last_crawled_at=parse_datetime(str(hit.payload["last_crawled_at"])),
            embedding_model=hit.payload.get("embedding_model"),
            chunking_version=hit.payload.get("chunking_version"),
            indexed_at=parse_optional_datetime(hit.payload.get("indexed_at")),
        ),
        score=hit.score,
    )


def parse_optional_datetime(value: object) -> datetime | None:
    """Parse optional ISO datetimes from vector store payloads."""

    if value is None:
        return None
    return parse_datetime(str(value))


def parse_datetime(value: str) -> datetime:
    """Parse an ISO datetime from a vector store payload."""

    return datetime.fromisoformat(value)
