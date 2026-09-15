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
- Optional Qdrant-backed retrieval mode after live page indexing.
- Optional OpenAI embeddings provider for Qdrant indexing and retrieval.
- Optional OpenAI ReAct-style planner that decides whether to retrieve, clarify, answer directly, or route out of scope.
- Optional OpenAI grounded answer generation from retrieved source excerpts.

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
- CLI path for creating the Qdrant collection and upserting allowlisted page chunks.
- OpenAI embeddings boundary using `text-embedding-3-small` by default when enabled.
- OpenAI ReAct-style planner boundary using `gpt-5-mini` by default when enabled.
- OpenAI Responses API answer-generation boundary using `gpt-5-mini` by default when enabled.

### Evaluation

- Golden-question dataset for deterministic chat behavior.
- Local evaluation runner.
- Tests covering safety, query rewrite, retrieval, citations, indexing, API behavior, and evaluation.

## Not Implemented

- Production Qdrant payload indexes.
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

Qdrant mode uses an explicit indexing step before chat:

```text
Allowlisted live pages
  -> Crawler
  -> Extractor
  -> Chunker
  -> Local deterministic embeddings
  -> Qdrant collection
  -> POST /api/chat with HARBOR_RETRIEVAL_MODE=qdrant
  -> Qdrant vector search
  -> AnswerComposer
```

With `HARBOR_EMBEDDING_PROVIDER=openai`, the Qdrant flow uses OpenAI embeddings
instead of the local deterministic embedding fixture. Use a separate Qdrant
collection such as `harbor_healthcare_chunks_openai` because vector dimensions
must match the embedding model.

With `HARBOR_ANSWER_PROVIDER=openai`, Harbor sends the retrieved source excerpts
to the OpenAI Responses API and asks for a concise cited answer grounded only in
those excerpts.

With `HARBOR_AGENT_PROVIDER=openai`, Harbor first asks the planner whether the
turn should call the healthcare retrieval tool. The planner can choose
`retrieve`, `clarify`, `direct_answer`, `out_of_scope`, or `safety`.

Default mode uses the local demo fixture:

```bash
uvicorn app.main:app --reload
```

Live ingestion mode fetches allowlisted pages and builds an in-memory index before answering:

```bash
HARBOR_RETRIEVAL_MODE=live uvicorn app.main:app --reload
```

Qdrant mode searches a local Qdrant collection populated by the ingestion CLI:

```bash
python -m app.ingestion.cli --write-to-qdrant --default-live-urls
HARBOR_RETRIEVAL_MODE=qdrant uvicorn app.main:app --reload
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
