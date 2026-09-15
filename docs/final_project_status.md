# Harbor Final Project Status

Harbor is an agentic RAG web app for Ontario healthcare navigation. It is built
as a local portfolio/demo project, not a production healthcare service.

## Final Showcase Path

The final intended path is:

```text
Trusted Ontario healthcare pages
  -> allowlist crawler
  -> HTML extraction
  -> metadata-aware chunking
  -> OpenAI embeddings
  -> Qdrant vector database
  -> OpenAI ReAct-style planner
  -> healthcare retrieval tool when needed
  -> OpenAI grounded answer generation
  -> cited chat response
```

## Implemented

- React/Vite chat UI.
- FastAPI backend.
- Trusted source registry and URL allowlist checks.
- Single-page crawler for approved healthcare source URLs.
- HTML extraction and metadata-aware chunking.
- Qdrant point mapping, collection creation, indexing, and retrieval.
- OpenAI embeddings with `text-embedding-3-small`.
- Query rewrite before retrieval.
- OpenAI ReAct-style planner that can choose:
  - `retrieve`
  - `clarify`
  - `direct_answer`
  - `out_of_scope`
  - `safety`
- Healthcare retrieval tool boundary.
- OpenAI grounded answer generation with citations.
- Emergency and out-of-scope safety routing.
- Golden-question evaluation.
- Local deterministic fallbacks for development and testing without paid API calls.

## Runtime Modes

### Local Demo Mode

Uses hand-written demo chunks. It does not require Docker, Qdrant, or OpenAI.
This mode is a development fallback for quick UI and API testing.

### Local Qdrant Mode

Uses real crawled/chunked source pages and Qdrant, but keeps local deterministic
embedding and answer behavior. This proves the ingestion and vector database
path during development without paid API calls.

### Final AI Mode

Uses OpenAI embeddings, Qdrant retrieval, OpenAI ReAct-style planning, and
OpenAI grounded answer generation. This is the main portfolio/resume version.

Required settings:

```bash
export OPENAI_API_KEY="your_api_key_here"
export HARBOR_EMBEDDING_PROVIDER=openai
export HARBOR_OPENAI_EMBEDDING_MODEL=text-embedding-3-small
export HARBOR_QDRANT_COLLECTION=harbor_healthcare_chunks_openai
export HARBOR_AGENT_PROVIDER=openai
export HARBOR_ANSWER_PROVIDER=openai
export HARBOR_LLM_MODEL=gpt-5-mini
```

## Resume-Ready Summary

Built an agentic RAG web application for Ontario healthcare navigation using
React, FastAPI, Qdrant, trusted-source crawling, OpenAI embeddings, ReAct-style
tool routing, grounded LLM answer generation, citations, and safety fallbacks.

## Remaining Non-Core Improvements

These are useful future improvements, but not required for the MVP showcase:

- Add a real reranker after Qdrant retrieval.
- Expand the allowlisted source set.
- Improve extraction for JavaScript-heavy pages such as Health811.
- Add scheduled source refresh and incremental re-indexing.
- Add retrieval observability logs or a small evaluation dashboard.
- Add multilingual support.
- Add location-aware clinic discovery.
- Add a fuller multi-step ReAct loop that can call retrieval more than once.

## Scope Notes

Harbor should not be presented as a medical diagnosis or emergency triage tool.
It is a navigation assistant that helps users find and understand trusted
Ontario healthcare information.
