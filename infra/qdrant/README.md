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
