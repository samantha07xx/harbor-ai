# Current State

Harbor is currently a local MVP/demo, not a production healthcare product.

## Implemented

### Frontend

- React and TypeScript chat UI.
- Session-only message history.
- Suggested follow-up buttons.
- Source citation rendering.
- Runtime badges showing local/pre-LLM demo status.
- Response metadata badges for safety, intent, and retrieval tool status.

### Backend

- FastAPI application with `GET /health`, `POST /api/chat`, and `POST /api/retrieval/search`.
- Environment-backed settings.
- Deterministic pre-LLM agent orchestrator.
- Lightweight safety/scope policy for emergency and clearly out-of-scope questions.
- Agent-facing healthcare retrieval tool.
- Query rewrite, deterministic embeddings, in-memory vector search, and cited draft answer composition.
- Local demo retrieval fixture for Health811, OHIP, newcomers, and emergency care.
- Optional live-ingested local retrieval mode from allowlisted Ontario healthcare pages.

### Ingestion

- Trusted source registry.
- URL allowlist checks.
- Guarded single-page fetch.
- HTML extraction.
- Metadata-aware chunking.
- Deterministic embedding boundary.
- Qdrant-ready point mapping.
- Indexing service boundary with in-memory test double.
- CLI dry-run for fetch/extract/chunk/embed/index preview.

### Evaluation

- Golden-question dataset for deterministic chat behavior.
- Local evaluation runner.
- Tests covering safety, query rewrite, retrieval, citations, indexing, API behavior, and evaluation.

## Not Implemented

- Production Qdrant collection creation and live indexed corpus.
- External embedding API calls.
- LLM-based answer generation.
- LLM-based ReAct or LangGraph agent loop.
- Recursive crawling.
- Batch indexing.
- Conversation persistence.
- User accounts or auth.
- Deployment.

## Local Demo Flow

```text
Frontend chat
  -> POST /api/chat
  -> DeterministicHealthcareAgent
  -> SafetyPolicy
  -> HealthcareRetrievalTool
  -> QueryRewriteService
  -> Deterministic embedding
  -> In-memory vector search over demo chunks or live-ingested chunks
  -> AnswerComposer
  -> ChatResponse with citations and metadata
```

Default mode uses the local demo fixture:

```bash
uvicorn app.main:app --reload
```

Live ingestion mode fetches allowlisted pages and builds an in-memory index before answering:

```bash
HARBOR_RETRIEVAL_MODE=live uvicorn app.main:app --reload
```

## Demo Questions

- `Can I call someone if it is not an emergency?`
- `How do I get a health card?`
- `I just landed and need a doctor. What can I do?`
- `I have chest pain and cannot breathe`
- `What is the weather tomorrow?`

## Verification

From `backend/`:

```bash
.venv/bin/pytest
.venv/bin/ruff check . ../tests/backend ../tests/ingestion ../tests/retrieval
python -m app.evaluation.run_eval
```

From `frontend/`:

```bash
npm run build
```
