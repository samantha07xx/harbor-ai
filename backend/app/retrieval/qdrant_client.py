"""Qdrant point mapping and vector store boundary.

Step 16 adds a live-client interface and test doubles. Unit tests use mocks or
in-memory storage, so Docker is not required.
"""

from datetime import datetime
from hashlib import sha256
from math import sqrt
from typing import Any, Protocol

import httpx
from pydantic import BaseModel, Field

from app.config import get_settings
from app.retrieval.embeddings import EmbeddingResult
from app.schemas.chunks import SourceChunk


class QdrantPoint(BaseModel):
    """Qdrant-ready point payload for one embedded source chunk."""

    id: str = Field(min_length=1)
    vector: list[float] = Field(min_length=1)
    payload: dict[str, Any]


class QdrantSearchHit(BaseModel):
    """Search hit returned from Qdrant or a compatible test double."""

    id: str
    score: float
    payload: dict[str, Any]


class VectorStore(Protocol):
    """Vector database boundary used by retrieval and indexing code."""

    def upsert_points(self, points: list[QdrantPoint]) -> None:
        """Store Qdrant-ready points."""

    def search(self, vector: list[float], *, limit: int = 6) -> list[QdrantSearchHit]:
        """Search for nearby points."""


class QdrantVectorStore:
    """Minimal HTTP client for Qdrant's REST API."""

    def __init__(
        self,
        *,
        url: str | None = None,
        collection_name: str | None = None,
        api_key: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        settings = get_settings()
        self.url = (url or settings.qdrant_url).rstrip("/")
        self.collection_name = collection_name or settings.qdrant_collection
        self.api_key = api_key if api_key is not None else settings.qdrant_api_key
        self._http_client = http_client

    def upsert_points(self, points: list[QdrantPoint]) -> None:
        """Upsert points into Qdrant."""

        if not points:
            return

        client = self._client()
        response = client.put(
            f"{self.url}/collections/{self.collection_name}/points",
            headers=self._headers(),
            json={"points": [point.model_dump(mode="json") for point in points]},
        )
        response.raise_for_status()

    def search(self, vector: list[float], *, limit: int = 6) -> list[QdrantSearchHit]:
        """Search Qdrant for similar points."""

        if not vector:
            raise ValueError("Search vector cannot be empty")

        client = self._client()
        response = client.post(
            f"{self.url}/collections/{self.collection_name}/points/search",
            headers=self._headers(),
            json={
                "vector": vector,
                "limit": limit,
                "with_payload": True,
            },
        )
        response.raise_for_status()
        body = response.json()
        return [
            QdrantSearchHit(
                id=str(hit["id"]),
                score=float(hit["score"]),
                payload=hit.get("payload") or {},
            )
            for hit in body.get("result", [])
        ]

    def _client(self) -> httpx.Client:
        """Return the configured HTTP client."""

        return self._http_client or httpx.Client(timeout=10.0)

    def _headers(self) -> dict[str, str]:
        """Return Qdrant request headers."""

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["api-key"] = self.api_key
        return headers


class InMemoryVectorStore:
    """Deterministic vector store test double."""

    def __init__(self) -> None:
        self.points: dict[str, QdrantPoint] = {}

    def upsert_points(self, points: list[QdrantPoint]) -> None:
        """Store points in memory."""

        for point in points:
            self.points[point.id] = point

    def search(self, vector: list[float], *, limit: int = 6) -> list[QdrantSearchHit]:
        """Search points by cosine similarity."""

        if not vector:
            raise ValueError("Search vector cannot be empty")

        hits = [
            QdrantSearchHit(
                id=point.id,
                score=cosine_similarity(vector, point.vector),
                payload=point.payload,
            )
            for point in self.points.values()
        ]
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:limit]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Return cosine similarity for equal-length vectors."""

    if len(left) != len(right):
        raise ValueError("Vectors must have the same dimensions")

    left_magnitude = sqrt(sum(value * value for value in left))
    right_magnitude = sqrt(sum(value * value for value in right))
    if left_magnitude == 0 or right_magnitude == 0:
        return 0.0

    dot_product = sum(
        left_value * right_value
        for left_value, right_value in zip(left, right, strict=True)
    )
    return dot_product / (left_magnitude * right_magnitude)


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
