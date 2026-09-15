# Infrastructure

Local infrastructure for Harbor.

Current status: Step 4 Qdrant environment scaffold.

Run Qdrant locally:

```bash
cd infra
docker compose up -d qdrant
```

Check that Qdrant is responding:

```bash
curl http://localhost:6333/healthz
```

Stop Qdrant:

```bash
cd infra
docker compose down
```

This step does not create collections, embeddings, or indexed healthcare chunks yet.
