# Qdrant

Local vector database target for Harbor.

Target collection name from the design baseline: `harbor_healthcare_chunks`.

The planned collection configuration is documented in `collection.config.json`.

Collection creation is handled by the local ingestion CLI when `--write-to-qdrant` is used, because Qdrant vector size must match the embedding model output dimension.

Planned distance metric: cosine similarity.

Planned payload index fields:

- `source_domain`
- `source_url`
- `topic`
- `trust_tier`
- `jurisdiction`
- `language`
- `last_crawled_at`

Step 14 defines the Python mapping from embedded chunks into Qdrant-ready points.
It still does not connect to or write to a live Qdrant instance.

Step 15 adds a dry-run indexing pipeline that produces Qdrant-ready points for one approved page, still without live Qdrant writes.

Step 16 adds a vector store boundary for Qdrant and an in-memory test double. Unit tests still do not require Docker.

Step 17 adds an indexing service that can upsert prepared points through that vector store boundary. Tests still use the in-memory store.

Step 18 adds retrieval over the vector store boundary. Tests still use the in-memory store rather than Docker.

Step 19 adds deterministic query rewrite before retrieval. Tests still use local deterministic components.

Step 20 composes query rewrite with retrieval. Tests still use local deterministic components and the in-memory vector store.

Step 21 exposes a retrieval testing API endpoint backed by a local demo in-memory index. It still does not require Docker.

Step 22 adds deterministic cited answer drafting from retrieved chunks. It still does not require Docker.

Step 23 wires the chat endpoint to the local retrieval and cited draft answer path. It still does not require Docker.

Step 24 adds a lightweight safety and scope layer before local chat retrieval. It still does not require Docker.

Step 25 adds an agent-facing retrieval tool boundary over the local retrieval path. It still does not require Docker.

Step 26 routes chat through a deterministic pre-LLM agent orchestrator. It still does not require Docker.

Step 27 adds golden-question evaluation for the deterministic local chat path. It still does not require Docker.

Step 28 adds an ingestion dry-run CLI that previews Qdrant-ready points without writing to Qdrant. It still does not require Docker.

The current Qdrant path can create the collection, upsert allowlisted live page chunks, and let the backend search that collection with `HARBOR_RETRIEVAL_MODE=qdrant`.

Local run:

```bash
cd infra
docker compose up -d qdrant
cd ../backend
source .venv/bin/activate
python -m app.ingestion.cli --write-to-qdrant --default-live-urls
HARBOR_RETRIEVAL_MODE=qdrant uvicorn app.main:app --reload
```

The default local Qdrant path uses a deterministic keyword fixture. To use real
OpenAI embeddings, set `HARBOR_EMBEDDING_PROVIDER=openai`,
`OPENAI_API_KEY`, and a separate collection name such as
`HARBOR_QDRANT_COLLECTION=harbor_healthcare_chunks_openai` before indexing.
