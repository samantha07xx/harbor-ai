"""Retrieval service for vector-store-backed healthcare chunks.

Step 18 embeds a query, searches the vector store, and maps hits into
RetrievalResult. It does not rewrite queries or call an agent.
"""

from datetime import datetime

from app.retrieval.embeddings import EmbeddingService
from app.retrieval.qdrant_client import QdrantSearchHit, VectorStore
from app.schemas.chunks import RetrievalHit, RetrievalResult, SourceChunk


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
