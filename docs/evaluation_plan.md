# Evaluation Plan

Harbor evaluation starts with a small hand-written set of common Ontario healthcare navigation questions in `backend/app/evaluation/golden_questions.json`.

Current checks:

- Retrieval relevance
- Citation coverage
- Answer grounding
- Scope control
- Safety behavior for medical or emergency questions

Run the local deterministic evaluation from `backend/`:

```bash
python -m app.evaluation.run_eval
```

The first dataset is intentionally small. It protects the MVP path while ingestion, retrieval, and agent orchestration are still local and deterministic.
