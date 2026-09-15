# Harbor Backend

Backend: Python, FastAPI, and Pydantic.

Current status: Step 21 local retrieval API foundation.

Implemented:

- FastAPI application factory
- `GET /health`
- Placeholder `POST /api/chat`
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

Not implemented yet:

- Agent loop
- External embedding API calls
- Live Qdrant-backed retrieval verification
- Recursive crawling
- Batch source indexing
- Production Qdrant collection management
- Grounded answer generation

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
