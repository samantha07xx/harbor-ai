# Harbor Backend

Backend: Python, FastAPI, and Pydantic.

Current status: minimal Step 2 service skeleton.

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

Not implemented yet:

- Agent loop
- Query rewrite
- Embeddings
- Qdrant retrieval
- Recursive crawling
- Embeddings
- Source indexing
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
