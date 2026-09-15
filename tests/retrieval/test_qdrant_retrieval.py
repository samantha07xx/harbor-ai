from app.retrieval.demo import LocalKeywordEmbeddingProvider, make_demo_chunks
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.qdrant import build_qdrant_rewritten_retrieval_service
from app.retrieval.qdrant_client import InMemoryVectorStore, map_chunk_to_qdrant_point


def test_qdrant_retrieval_service_uses_qdrant_corpus_mode() -> None:
    embedding_service = EmbeddingService(LocalKeywordEmbeddingProvider())
    vector_store = InMemoryVectorStore()
    vector_store.upsert_points(
        [
            map_chunk_to_qdrant_point(chunk, embedding_service.embed_chunk(chunk))
            for chunk in make_demo_chunks()
        ]
    )
    retrieval_service = build_qdrant_rewritten_retrieval_service(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    result = retrieval_service.retrieve("How do I apply for a health card?", limit=1)

    assert retrieval_service.corpus_mode == "qdrant"
    assert result.retrieval.hits[0].chunk.title == "Apply for OHIP and get a health card"
