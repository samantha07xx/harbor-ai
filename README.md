# Harbor

Harbor is a planned AI-powered Ontario healthcare navigation web app for newcomers. The product will provide a simple chat interface backed by an agentic RAG system grounded in trusted official and public healthcare sources.

This repository is currently at Step 2: minimal backend foundation. It contains structure, configuration placeholders, planning documents, and a runnable FastAPI backend skeleton. Crawling, retrieval, indexing, and agent logic are intentionally not implemented yet.

## Design Baseline

The source design document is kept at:

- `docs/harbor_project_documentation.md`

Build decisions should follow that document unless a later commit updates the architecture.

## Planned Stack

- Frontend: React with TypeScript
- Backend: Python with FastAPI and Pydantic
- Agent/RAG: lightweight ReAct loop or LangGraph later
- Vector database: Qdrant
- Ingestion: allowlist crawler, content extraction, metadata-aware chunking, embeddings
- Evaluation: small golden question set and retrieval/citation checks

## Current Structure

```text
docs/       Project documentation and architecture notes
frontend/   Planned web chat UI
backend/    Planned FastAPI service and RAG modules
infra/      Planned local infrastructure such as Qdrant
tests/      Planned backend, retrieval, and ingestion tests
```

## Current Status

Completed:

- Clean Harbor repository structure
- Design document copied into `docs/`
- Minimal backend, frontend, infra, and test placeholders
- Environment variable example file
- Git ignore rules for local development artifacts
- Runnable FastAPI app skeleton
- `GET /health`
- Placeholder `POST /api/chat`

Not implemented yet:

- Backend chat API
- Frontend chat UI
- Qdrant runtime
- Crawling or ingestion
- Embeddings
- Retrieval
- Agent loop
- Grounded answer generation

## Next Step

Step 3 should set up the simple frontend chat shell that can later connect to the backend.
