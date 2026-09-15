# Harbor Backend

Backend: Python, FastAPI, and Pydantic.

Current status: local deterministic Harbor backend demo.

Implemented:

- FastAPI application factory
- `GET /health`
- Pre-agent local RAG `POST /api/chat`
- Environment-backed settings
- Core trusted source and chunk schemas
- Trusted source registry loader
- Crawler interface with URL allowlist checks
- Fetch-free HTML extraction contract
- Guarded single-page HTML fetching
- Single-page fetch-and-extract ingestion service
- Metadata-aware chunking for extracted pages
- Single-page fetch-extract-chunk ingestion service
- Embedding service interface and deterministic test provider
- Qdrant point mapping for embedded chunks
- Dry-run indexing pipeline for one approved page
- Live Qdrant vector store interface with test doubles
- Indexing service that upserts through the vector store boundary
- Retrieval service for query embedding and vector search
- Lightweight deterministic query rewrite service
- Rewrite-plus-retrieval composition service
- Local `POST /api/retrieval/search` endpoint backed by a demo in-memory index
- Deterministic cited answer composer for retrieved chunks
- Chat endpoint wired to local retrieval and cited draft answers
- Lightweight emergency and out-of-scope safety response layer
- Agent-facing healthcare retrieval tool boundary
- Deterministic pre-LLM agent orchestrator
- Golden-question evaluation runner
- Ingestion dry-run CLI for fetch/extract/chunk/embed/index preview

Not implemented yet:

- Full LLM-based agent loop
- External embedding API calls
- Live Qdrant-backed retrieval verification
- Recursive crawling
- Batch source indexing
- Production Qdrant collection management
- LLM-based grounded answer generation

Run locally from this folder:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Then visit:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

Local retrieval endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/retrieval/search \
  -H "Content-Type: application/json" \
  -d '{"question":"Can I call someone if it is not an emergency?","limit":1}'
```

Local chat endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"local-test","message":"Can I call someone if it is not an emergency?","user_context":{"province":"Ontario"}}'
```

Local evaluation:

```bash
python -m app.evaluation.run_eval
```

Ingestion dry-run:

```bash
python -m app.ingestion.cli --url https://www.ontario.ca/page/apply-ohip-and-get-health-card
```

For fully offline testing, pass `--fixture-html path/to/page.html`.
