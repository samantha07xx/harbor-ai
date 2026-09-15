"""Dry-run indexing pipeline.

Step 15 composes one-page ingestion, chunking, embedding, and Qdrant point
mapping. It does not connect to or write to a live Qdrant instance.
"""

from dataclasses import dataclass

from app.ingestion.chunker import ChunkingSettings
from app.ingestion.page_ingestion import ChunkedPageIngestionResult, PageIngestionService
from app.retrieval.embeddings import EmbeddingResult, EmbeddingService
from app.retrieval.qdrant_client import QdrantPoint, map_chunks_to_qdrant_points


@dataclass(frozen=True)
class DryRunIndexingResult:
    """Artifacts produced by the dry-run indexing pipeline."""

    page_result: ChunkedPageIngestionResult
    embeddings: list[EmbeddingResult]
    points: list[QdrantPoint]

    @property
    def chunk_count(self) -> int:
        """Return the number of chunks produced."""

        return len(self.page_result.chunks)

    @property
    def point_count(self) -> int:
        """Return the number of Qdrant-ready points produced."""

        return len(self.points)


class DryRunIndexer:
    """Build Qdrant-ready points without writing them anywhere."""

    def __init__(
        self,
        page_ingestion_service: PageIngestionService,
        embedding_service: EmbeddingService,
    ) -> None:
        self.page_ingestion_service = page_ingestion_service
        self.embedding_service = embedding_service

    def prepare_one_page(
        self,
        url: str,
        *,
        chunking_settings: ChunkingSettings | None = None,
    ) -> DryRunIndexingResult:
        """Prepare one approved page for future indexing."""

        page_result = self.page_ingestion_service.ingest_one_page_chunks(
            url,
            chunking_settings=chunking_settings,
        )
        embeddings = [self.embedding_service.embed_chunk(chunk) for chunk in page_result.chunks]
        points = map_chunks_to_qdrant_points(list(zip(page_result.chunks, embeddings, strict=True)))

        return DryRunIndexingResult(
            page_result=page_result,
            embeddings=embeddings,
            points=points,
        )
