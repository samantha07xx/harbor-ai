# Harbor

Harbor is a local demo of an AI-assisted Ontario healthcare navigation app for newcomers. It provides a web chat UI backed by ReAct-style tool planning, source-grounded retrieval, citations, safety/scope routing, live allowlisted ingestion, optional Qdrant-backed retrieval, optional OpenAI embeddings, optional OpenAI grounded answer generation, ingestion dry-runs, and golden-question evaluation.

The original design baseline lives in `docs/harbor_project_documentation.md`.
The final implemented project status is summarized in `docs/final_project_status.md`.
The detailed current implementation notes live in `docs/current_state.md`.

## What Works Now

- React/Vite chat UI at `http://127.0.0.1:5173`
- FastAPI backend at `http://127.0.0.1:8000`
- Deterministic pre-LLM agent for local demo behavior
- Safety/scope routing for emergency and clearly out-of-scope questions
- Local demo retrieval index with cited answers
- Optional live-ingested retrieval mode from allowlisted Ontario healthcare pages
- Optional Qdrant-backed retrieval mode after indexing allowlisted pages
- Optional OpenAI embeddings provider for Qdrant indexing and search
- Optional OpenAI ReAct-style planner that decides whether to call retrieval
- Optional OpenAI grounded answer generation from retrieved source excerpts
- Trusted source registry and URL allowlist checks
- One-page fetch, extraction, chunking, embedding, Qdrant-point preview, and Qdrant upsert CLI
- Golden-question evaluation for deterministic chat behavior

## Run The Demo

Start the backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

To use real allowlisted web pages instead of the hand-written demo fixture:

```bash
cd backend
source .venv/bin/activate
HARBOR_RETRIEVAL_MODE=live uvicorn app.main:app --reload
```

To use Qdrant-backed retrieval, first start Qdrant and index the allowlisted pages:

```bash
cd infra
docker compose up -d qdrant
cd ../backend
source .venv/bin/activate
python -m app.ingestion.cli --write-to-qdrant --default-live-urls
HARBOR_RETRIEVAL_MODE=qdrant uvicorn app.main:app --reload
```

To rebuild Qdrant with OpenAI embeddings, use a separate collection because OpenAI
embedding vectors have different dimensions from the local keyword fixture:

```bash
cd backend
source .venv/bin/activate
export OPENAI_API_KEY="your_api_key_here"
export HARBOR_EMBEDDING_PROVIDER=openai
export HARBOR_OPENAI_EMBEDDING_MODEL=text-embedding-3-small
export HARBOR_QDRANT_COLLECTION=harbor_healthcare_chunks_openai
python -m app.ingestion.cli --write-to-qdrant --default-live-urls
export HARBOR_AGENT_PROVIDER=openai
export HARBOR_ANSWER_PROVIDER=openai
export HARBOR_LLM_MODEL=gpt-5-mini
HARBOR_RETRIEVAL_MODE=qdrant uvicorn app.main:app --reload
```

Start the frontend in a second terminal:

```bash
cd frontend
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

Try:

- `Can I call someone if it is not an emergency?`
- `How do I get a health card?`
- `I just landed and need a doctor. What can I do?`
- `What is the weather tomorrow?`

## Useful Commands

Run backend tests:

```bash
cd backend
.venv/bin/pytest
.venv/bin/ruff check . ../tests/backend ../tests/ingestion ../tests/retrieval
```

Run frontend build:

```bash
cd frontend
npm run build
```

Run deterministic evaluation:

```bash
cd backend
python -m app.evaluation.run_eval
```

Run ingestion dry-run:

```bash
cd backend
python -m app.ingestion.cli --url https://www.ontario.ca/page/apply-ohip-and-get-health-card
```

Index the default live allowlisted pages into Qdrant:

```bash
cd backend
python -m app.ingestion.cli --write-to-qdrant --default-live-urls
```

## Current Limits

- Qdrant-backed retrieval is wired, but it requires a running local Qdrant instance and an indexing step before use.
- External embedding and LLM calls are optional and only run when OpenAI environment variables are configured.
- By default, chat uses a tiny local demo retrieval fixture. Set `HARBOR_RETRIEVAL_MODE=live` to build an in-memory index from real allowlisted pages at startup.
- Set `HARBOR_RETRIEVAL_MODE=qdrant` after indexing to search the configured Qdrant collection.
- Live mode is still local and deterministic. Qdrant mode can use either the local keyword fixture or OpenAI embeddings.
- LLM answer generation is optional and off by default. Set `HARBOR_ANSWER_PROVIDER=openai` to use OpenAI grounded answer generation from retrieved source excerpts.
- ReAct-style planning is optional and off by default. Set `HARBOR_AGENT_PROVIDER=openai` to let the agent decide whether to retrieve, clarify, answer directly, or route out of scope.
- By default, the agent uses local deterministic routing. With `HARBOR_AGENT_PROVIDER=openai`, it uses an OpenAI ReAct-style planner.
- The ingestion pipeline is single-page and dry-run oriented. It does not recursively crawl sites.

## Repo Map

```text
backend/   FastAPI app, deterministic agent, retrieval, ingestion, evaluation
frontend/  React/Vite chat UI
docs/      Design baseline, current state, architecture, evaluation notes
infra/     Local Qdrant scaffold
tests/     Backend, ingestion, and retrieval tests
```
