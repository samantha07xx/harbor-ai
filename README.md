# Harbor

Harbor is a planned AI-powered Ontario healthcare navigation web app for newcomers. The product will provide a simple chat interface backed by an agentic RAG system grounded in trusted official and public healthcare sources.

This repository is currently at Step 5: minimal frontend/backend foundation, local Qdrant infrastructure scaffold, and core data schemas. It contains structure, planning documents, a runnable FastAPI backend skeleton, a React chat shell, Docker Compose for local Qdrant, and Pydantic models for trusted sources, pages, chunks, and retrieval results. Crawling, retrieval, indexing, and agent logic are intentionally not implemented yet.

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
- Runnable React/Vite chat shell
- Frontend API client for backend chat requests
- Local Qdrant Docker Compose service
- Planned Qdrant collection configuration notes
- Core trusted source, source page, chunk, citation, and retrieval result schemas

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

Step 6 should create the first trusted source registry file from approved Ontario healthcare seed URLs, without crawling yet.
