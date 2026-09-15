# Harbor Architecture Notes

This file is a working companion to `harbor_project_documentation.md`.

Current implementation status: scaffold only.

Planned architecture:

1. Offline ingestion pipeline crawls trusted Ontario healthcare sources.
2. Extracted pages are cleaned, enriched with metadata, chunked, embedded, and indexed into Qdrant.
3. Runtime chat API receives user questions from the web UI.
4. Agentic RAG flow rewrites queries, retrieves source-backed chunks, checks sufficiency, and generates cited answers.

No architecture code is implemented in Step 1.
