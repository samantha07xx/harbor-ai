"""Embedding service interfaces and deterministic test provider.

Step 13 defines how text and chunks enter the embedding layer. It does not call
external embedding APIs.
"""

from dataclasses import dataclass
from hashlib import sha256
from math import sqrt
from typing import Protocol

from app.config import get_settings
from app.schemas.chunks import SourceChunk


@dataclass(frozen=True)
class EmbeddingRequest:
    """Text payload sent to an embedding provider."""

    text: str
    model: str


@dataclass(frozen=True)
class EmbeddingResult:
    """Vector returned by an embedding provider."""

    text: str
    model: str
    vector: list[float]

    @property
    def dimensions(self) -> int:
        """Return vector dimensionality."""

        return len(self.vector)


class EmbeddingProvider(Protocol):
    """Protocol implemented by embedding providers."""

    model: str

    def embed_text(self, text: str) -> EmbeddingResult:
        """Embed one text payload."""


class DeterministicEmbeddingProvider:
    """Stable local embedding provider for tests and development wiring.

    This is not semantically meaningful. It exists so the retrieval pipeline can
    be developed without making paid or networked embedding calls.
    """

    def __init__(self, *, model: str = "deterministic-test-embedding", dimensions: int = 16) -> None:
        self.model = model
        self.dimensions = dimensions

    def embed_text(self, text: str) -> EmbeddingResult:
        """Create a stable normalized vector from text."""

        if not text.strip():
            raise ValueError("Cannot embed empty text")

        digest = sha256(text.encode("utf-8")).digest()
        values = [
            ((digest[index % len(digest)] / 255.0) * 2.0) - 1.0
            for index in range(self.dimensions)
        ]
        magnitude = sqrt(sum(value * value for value in values)) or 1.0
        vector = [value / magnitude for value in values]

        return EmbeddingResult(
            text=text,
            model=self.model,
            vector=vector,
        )


class EmbeddingService:
    """Application embedding boundary."""

    def __init__(self, provider: EmbeddingProvider | None = None) -> None:
        settings = get_settings()
        self.provider = provider or DeterministicEmbeddingProvider(
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
        )

    def embed_query(self, query: str) -> EmbeddingResult:
        """Embed a rewritten retrieval query."""

        return self.provider.embed_text(query)

    def embed_chunk(self, chunk: SourceChunk) -> EmbeddingResult:
        """Embed a source chunk using the Harbor chunk text format."""

        return self.provider.embed_text(format_chunk_for_embedding(chunk))


def format_chunk_for_embedding(chunk: SourceChunk) -> str:
    """Format chunk metadata and content for embedding."""

    section = chunk.section_heading or "General"
    return "\n".join(
        [
            f"Title: {chunk.title}",
            f"Section: {section}",
            f"Topic: {chunk.topic}",
            f"Content: {chunk.text}",
        ]
    )
