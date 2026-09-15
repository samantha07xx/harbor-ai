"""Qdrant point mapping utilities.

Step 14 maps embedded source chunks to the structure Harbor will later send to
Qdrant. It does not connect to a live Qdrant instance.
"""

from datetime import datetime
from hashlib import sha256
from typing import Any

from pydantic import BaseModel, Field

from app.retrieval.embeddings import EmbeddingResult
from app.schemas.chunks import SourceChunk


class QdrantPoint(BaseModel):
    """Qdrant-ready point payload for one embedded source chunk."""

    id: str = Field(min_length=1)
    vector: list[float] = Field(min_length=1)
    payload: dict[str, Any]


def make_qdrant_point_id(chunk_id: str) -> str:
    """Create a deterministic Qdrant point ID from a chunk ID."""

    return sha256(chunk_id.encode("utf-8")).hexdigest()


def chunk_payload(chunk: SourceChunk, embedding: EmbeddingResult) -> dict[str, Any]:
    """Create the metadata payload Harbor will store in Qdrant."""

    return {
        "chunk_id": chunk.chunk_id,
        "page_id": chunk.page_id,
        "source_id": chunk.source_id,
        "source_domain": str(chunk.source_url.host or ""),
        "source_url": str(chunk.source_url),
        "title": chunk.title,
        "section_heading": chunk.section_heading,
        "topic": str(chunk.topic),
        "jurisdiction": str(chunk.jurisdiction),
        "language": str(chunk.language),
        "trust_tier": str(chunk.trust_tier),
        "chunk_index": chunk.chunk_index,
        "text": chunk.text,
        "token_count": chunk.token_count,
        "content_hash": chunk.content_hash,
        "last_crawled_at": serialize_datetime(chunk.last_crawled_at),
        "embedding_model": embedding.model,
        "embedding_dimensions": embedding.dimensions,
        "chunking_version": chunk.chunking_version,
        "indexed_at": serialize_datetime(chunk.indexed_at),
    }


def map_chunk_to_qdrant_point(chunk: SourceChunk, embedding: EmbeddingResult) -> QdrantPoint:
    """Map one embedded chunk to a Qdrant-ready point."""

    if not embedding.vector:
        raise ValueError("Embedding vector cannot be empty")

    return QdrantPoint(
        id=make_qdrant_point_id(chunk.chunk_id),
        vector=embedding.vector,
        payload=chunk_payload(chunk, embedding),
    )


def map_chunks_to_qdrant_points(
    chunks_and_embeddings: list[tuple[SourceChunk, EmbeddingResult]],
) -> list[QdrantPoint]:
    """Map many embedded chunks to Qdrant-ready points."""

    return [
        map_chunk_to_qdrant_point(chunk, embedding)
        for chunk, embedding in chunks_and_embeddings
    ]


def serialize_datetime(value: datetime | None) -> str | None:
    """Serialize optional datetimes for Qdrant payloads."""

    if value is None:
        return None
    return value.isoformat()
