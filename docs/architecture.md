# Architecture Notes

This file is a compact companion to `harbor_project_documentation.md`.

## Runtime Chat

```text
React chat UI
  -> FastAPI /api/chat
  -> DeterministicHealthcareAgent
  -> SafetyPolicy
  -> HealthcareRetrievalTool
  -> QueryRewriteService
  -> EmbeddingService
  -> VectorStore boundary
  -> AnswerComposer
  -> ChatResponse
```

The current runtime path is deterministic and local. It does not call an LLM, does not call an external embedding API, and does not require Qdrant.

## Ingestion

```text
Trusted source registry
  -> URL allowlist
  -> Single-page fetch
  -> HTML extraction
  -> Chunking
  -> Embedding
  -> Qdrant-ready point mapping
  -> Optional vector store upsert boundary
```

The current ingestion CLI is a dry-run preview. It can fetch a single allowlisted URL or read fixture HTML, then print a JSON summary of the artifacts it would prepare.

## Boundaries

- `app/api`: HTTP request/response routing.
- `app/agent`: orchestration, tools, and answer composition.
- `app/safety`: deterministic safety/scope routing.
- `app/retrieval`: query rewrite, embeddings, vector store boundary, retrieval services.
- `app/ingestion`: trusted source loading, crawl/fetch, extraction, chunking, indexing prep.
- `app/evaluation`: golden-question evaluation.

## Production Migration Points

- Replace deterministic embeddings with a real embedding provider.
- Replace the local demo retrieval fixture with indexed Qdrant data.
- Add production Qdrant collection creation and migrations.
- Replace the deterministic pre-LLM agent with an LLM-backed agent loop.
- Add source freshness monitoring and batch indexing.
