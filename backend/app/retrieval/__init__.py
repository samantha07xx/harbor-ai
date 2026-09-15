"""Retrieval and ranking modules."""

from app.retrieval.embeddings import (
    DeterministicEmbeddingProvider,
    EmbeddingProvider,
    EmbeddingRequest,
    EmbeddingResult,
    EmbeddingService,
    format_chunk_for_embedding,
)
from app.retrieval.live import (
    LiveIngestionRetrievalError,
    build_live_ingested_rewritten_retrieval_service,
    get_live_ingested_rewritten_retrieval_service,
    get_live_or_demo_rewritten_retrieval_service,
)
from app.retrieval.qdrant_client import (
    InMemoryVectorStore,
    QdrantPoint,
    QdrantSearchHit,
    QdrantVectorStore,
    VectorStore,
    chunk_payload,
    cosine_similarity,
    make_qdrant_point_id,
    map_chunk_to_qdrant_point,
    map_chunks_to_qdrant_points,
)
from app.retrieval.query_rewrite import (
    QueryIntent,
    QueryRewriteResult,
    QueryRewriteService,
    RewriteRule,
)
from app.retrieval.service import (
    RetrievalService,
    RewrittenRetrievalResult,
    RewrittenRetrievalService,
    map_search_hit_to_retrieval_hit,
)

__all__ = [
    "DeterministicEmbeddingProvider",
    "EmbeddingProvider",
    "EmbeddingRequest",
    "EmbeddingResult",
    "EmbeddingService",
    "InMemoryVectorStore",
    "LiveIngestionRetrievalError",
    "QdrantPoint",
    "QdrantSearchHit",
    "QdrantVectorStore",
    "QueryIntent",
    "QueryRewriteResult",
    "QueryRewriteService",
    "RetrievalService",
    "RewriteRule",
    "RewrittenRetrievalResult",
    "RewrittenRetrievalService",
    "VectorStore",
    "build_live_ingested_rewritten_retrieval_service",
    "chunk_payload",
    "cosine_similarity",
    "format_chunk_for_embedding",
    "get_live_ingested_rewritten_retrieval_service",
    "get_live_or_demo_rewritten_retrieval_service",
    "make_qdrant_point_id",
    "map_chunk_to_qdrant_point",
    "map_chunks_to_qdrant_points",
    "map_search_hit_to_retrieval_hit",
]
