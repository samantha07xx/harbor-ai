# Harbor

Harbor is an agentic RAG web app for Ontario healthcare navigation. It combines a React chat UI, FastAPI backend, trusted-source crawling, OpenAI embeddings, Qdrant vector search, ReAct-style tool planning, grounded OpenAI answer generation, citations, safety routing, and golden-question evaluation.

The original design baseline lives in `docs/harbor_project_documentation.md`.
The final implemented project status is summarized in `docs/final_project_status.md`.
The detailed current implementation notes live in `docs/current_state.md`.

## What Works Now

- React/Vite chat UI at `http://127.0.0.1:5173`
- FastAPI backend at `http://127.0.0.1:8000`
- Trusted source registry and allowlist-based crawler
- HTML extraction and metadata-aware chunking
- OpenAI embeddings for Qdrant indexing and search
- Qdrant-backed retrieval over trusted healthcare chunks
- Query rewrite before retrieval
- OpenAI ReAct-style planner that decides whether to retrieve, clarify, answer directly, or route out of scope
- Healthcare retrieval tool boundary
- OpenAI grounded answer generation from retrieved source excerpts
- Citations for source-backed answers
- Safety/scope routing for emergency and clearly out-of-scope questions
- Local deterministic fallbacks for development and testing without paid API calls
- Golden-question evaluation

## Run Final AI Mode

Start Qdrant:

```bash
cd /Users/samantha/Documents/Codex/2026-09-15/harbor-ai-repo/infra
docker compose up -d qdrant
curl http://localhost:6333/healthz
```

Index trusted pages with OpenAI embeddings, then start the backend:

```bash
cd /Users/samantha/Documents/Codex/2026-09-15/harbor-ai-repo/backend
source .venv/bin/activate

export OPENAI_API_KEY="your_api_key_here"
export HARBOR_EMBEDDING_PROVIDER=openai
export HARBOR_OPENAI_EMBEDDING_MODEL=text-embedding-3-small
export HARBOR_QDRANT_COLLECTION=harbor_healthcare_chunks_openai
python -m app.ingestion.cli --write-to-qdrant --default-live-urls
export HARBOR_AGENT_PROVIDER=openai
export HARBOR_ANSWER_PROVIDER=openai
export HARBOR_LLM_MODEL=gpt-5-mini
HARBOR_RETRIEVAL_MODE=qdrant uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start the frontend in a second terminal:

```bash
cd /Users/samantha/Documents/Codex/2026-09-15/harbor-ai-repo/frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

Try:

- `What can you help me with?`
- `Can I call someone if it is not an emergency?`
- `How do I get a health card?`
- `I just landed and need a doctor. What can I do?`
- `What is the weather tomorrow?`

## Development Fallbacks

Harbor also includes local fallback modes so the UI, API, ingestion pipeline, and tests can run without paid API calls:

- Local demo mode uses a tiny hand-written fixture.
- Live local mode builds an in-memory index from allowlisted pages.
- Local Qdrant mode writes real crawled chunks to Qdrant with deterministic local embeddings.

These modes are for development and testing. The portfolio showcase path is Final AI Mode.

## Useful Commands

Run backend tests:

```bash
cd /Users/samantha/Documents/Codex/2026-09-15/harbor-ai-repo/backend
.venv/bin/pytest
.venv/bin/ruff check . ../tests/backend ../tests/ingestion ../tests/retrieval
```

Run frontend build:

```bash
cd /Users/samantha/Documents/Codex/2026-09-15/harbor-ai-repo/frontend
npm run build
```

Run deterministic evaluation:

```bash
cd /Users/samantha/Documents/Codex/2026-09-15/harbor-ai-repo/backend
python -m app.evaluation.run_eval
```

Run ingestion dry-run:

```bash
cd /Users/samantha/Documents/Codex/2026-09-15/harbor-ai-repo/backend
python -m app.ingestion.cli --url https://www.ontario.ca/page/apply-ohip-and-get-health-card
```

Index the default live allowlisted pages into Qdrant:

```bash
cd /Users/samantha/Documents/Codex/2026-09-15/harbor-ai-repo/backend
python -m app.ingestion.cli --write-to-qdrant --default-live-urls
```

## Remaining Non-Core Improvements

- Add a real reranker after Qdrant retrieval.
- Expand the allowlisted source set.
- Improve extraction for JavaScript-heavy pages such as Health811.
- Add scheduled source refresh and incremental re-indexing.
- Add retrieval observability logs or a small evaluation dashboard.

## Repo Map

```text
backend/   FastAPI app, agent planner, retrieval, ingestion, evaluation
frontend/  React/Vite chat UI
docs/      Design baseline, current state, architecture, evaluation notes
infra/     Local Qdrant scaffold
tests/     Backend, ingestion, and retrieval tests
```
