"""Embedding service interfaces and local/OpenAI providers.

The default path stays local and deterministic. OpenAI embeddings are enabled
only when explicitly configured.
"""

from dataclasses import dataclass
from hashlib import sha256
from math import sqrt
from typing import Protocol

import httpx

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


class OpenAIEmbeddingProvider:
    """Embedding provider backed by OpenAI's embeddings API."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "text-embedding-3-small",
        base_url: str = "https://api.openai.com/v1",
        http_client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI embeddings")

        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._http_client = http_client

    def embed_text(self, text: str) -> EmbeddingResult:
        """Embed text using OpenAI's embeddings endpoint."""

        if not text.strip():
            raise ValueError("Cannot embed empty text")

        response = self._client().post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "input": text,
            },
        )
        response.raise_for_status()
        body = response.json()
        vector = body["data"][0]["embedding"]
        return EmbeddingResult(
            text=text,
            model=self.model,
            vector=[float(value) for value in vector],
        )

    def _client(self) -> httpx.Client:
        """Return the configured HTTP client."""

        return self._http_client or httpx.Client(timeout=30.0)


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


def build_configured_embedding_service(
    *,
    default_provider: str = "deterministic",
) -> EmbeddingService:
    """Build an embedding service from runtime settings."""

    settings = get_settings()
    provider_name = (settings.embedding_provider or default_provider).lower()
    if provider_name in {"deterministic", "local"}:
        return EmbeddingService(
            DeterministicEmbeddingProvider(
                model=settings.embedding_model,
                dimensions=settings.embedding_dimensions,
            )
        )
    if provider_name in {"local_keyword", "keyword"}:
        return EmbeddingService(LocalKeywordEmbeddingProvider())
    if provider_name == "openai":
        return EmbeddingService(
            OpenAIEmbeddingProvider(
                api_key=settings.openai_api_key or "",
                model=settings.openai_embedding_model,
                base_url=settings.openai_base_url,
            )
        )
    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")


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
