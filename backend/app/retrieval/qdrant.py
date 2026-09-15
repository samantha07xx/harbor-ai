"""Qdrant-backed retrieval service wiring."""

from functools import lru_cache

from app.retrieval.demo import LocalKeywordEmbeddingProvider
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.qdrant_client import QdrantVectorStore, VectorStore
from app.retrieval.query_rewrite import QueryRewriteService
from app.retrieval.service import RetrievalService, RewrittenRetrievalService


@lru_cache
def get_qdrant_rewritten_retrieval_service() -> RewrittenRetrievalService:
    """Build a cached retrieval service backed by the configured Qdrant collection."""

    return build_qdrant_rewritten_retrieval_service()


def build_qdrant_rewritten_retrieval_service(
    *,
    embedding_service: EmbeddingService | None = None,
    vector_store: VectorStore | None = None,
) -> RewrittenRetrievalService:
    """Build the Qdrant-backed rewrite-plus-retrieval path."""

    configured_embedding_service = embedding_service or EmbeddingService(
        LocalKeywordEmbeddingProvider()
    )
    return RewrittenRetrievalService(
        query_rewrite_service=QueryRewriteService(),
        retrieval_service=RetrievalService(
            embedding_service=configured_embedding_service,
            vector_store=vector_store or QdrantVectorStore(),
        ),
        corpus_mode="qdrant",
    )
