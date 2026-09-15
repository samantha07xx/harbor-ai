# Harbor Frontend

Frontend: React, TypeScript, and Vite.

Current status: chat shell connected to the deterministic local demo backend.

Implemented:

- Harbor chat page
- Session-only message history
- Message input and submit button
- Loading and error states
- Suggested prompt buttons
- API client for `POST /api/chat`
- Citation rendering from backend responses
- Runtime badges for local/pre-LLM demo status
- Response metadata badges for safety, intent, and retrieval tool status

Not implemented yet:

- Full agentic grounded RAG responses
- Citation rendering from indexed Qdrant sources
- Conversation persistence
- User accounts

Run locally from this folder:

```bash
npm install
npm run dev
```

The backend should be running at `http://127.0.0.1:8000`.
