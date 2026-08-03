from __future__ import annotations

import hashlib
import math
from typing import Protocol


DEFAULT_EMBEDDING_DIMENSIONS = 16


class EmbeddingService(Protocol):
    def embed_text(self, text: str) -> list[float]:
        """Return one embedding vector for one text string."""
        ...

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for a list of text strings."""
        ...


class MockEmbeddingService:
    """Local deterministic embedding service for early RAG development."""

    def __init__(self, dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS):
        if dimensions <= 0:
            raise ValueError("Embedding dimensions must be greater than 0.")

        self.dimensions = dimensions

    def embed_text(self, text: str) -> list[float]:
        values = self._hash_to_values(text.strip())
        return self._normalize(values)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]

    def _hash_to_values(self, text: str) -> list[float]:
        values: list[float] = []
        counter = 0
        text_bytes = text.encode("utf-8")

        while len(values) < self.dimensions:
            counter_bytes = counter.to_bytes(4, byteorder="big")
            digest = hashlib.sha256(text_bytes + counter_bytes).digest()

            for byte in digest:
                values.append((byte / 127.5) - 1.0)

                if len(values) == self.dimensions:
                    break

            counter += 1

        return values

    def _normalize(self, values: list[float]) -> list[float]:
        magnitude = math.sqrt(sum(value * value for value in values))

        if magnitude == 0:
            return values

        return [value / magnitude for value in values]


def get_embedding_service() -> EmbeddingService:
    return MockEmbeddingService()
