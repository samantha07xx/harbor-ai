# Harbor

Harbor is a local demo of an AI-assisted Ontario healthcare navigation app for newcomers. It provides a web chat UI backed by a deterministic pre-LLM agent, source-grounded retrieval fixtures, citations, safety/scope routing, ingestion dry-runs, and golden-question evaluation.

The original design baseline lives in `docs/harbor_project_documentation.md`. The current implemented state is summarized in `docs/current_state.md`.

## What Works Now

- React/Vite chat UI at `http://127.0.0.1:5173`
- FastAPI backend at `http://127.0.0.1:8000`
- Deterministic pre-LLM agent for local demo behavior
- Safety/scope routing for emergency and clearly out-of-scope questions
- Local demo retrieval index with cited answers
- Trusted source registry and URL allowlist checks
- One-page fetch, extraction, chunking, embedding, and Qdrant-point preview
- Golden-question evaluation for deterministic chat behavior

## Run The Demo

Start the backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
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

## Current Limits

- No production Qdrant collection is required or populated yet.
- No external embedding API or LLM API is called.
- The chat answer path uses a tiny local demo retrieval fixture, not a full crawled corpus.
- The agent is deterministic and pre-LLM; it is shaped like an agent boundary but does not reason with a model.
- The ingestion pipeline is single-page and dry-run oriented. It does not recursively crawl sites.

## Repo Map

```text
backend/   FastAPI app, deterministic agent, retrieval, ingestion, evaluation
frontend/  React/Vite chat UI
docs/      Design baseline, current state, architecture, evaluation notes
infra/     Local Qdrant scaffold
tests/     Backend, ingestion, and retrieval tests
```
