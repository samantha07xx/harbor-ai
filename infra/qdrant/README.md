# Qdrant

Local vector database target for Harbor.

Target collection name from the design baseline: `harbor_healthcare_chunks`.

The planned collection configuration is documented in `collection.config.json`.

Collection creation is intentionally deferred until the embedding model is selected, because Qdrant vector size must match the embedding model output dimension.

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
