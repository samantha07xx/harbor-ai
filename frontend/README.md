# Harbor Frontend

Frontend: React, TypeScript, and Vite.

Current status: Step 23 chat shell connected to the pre-agent local RAG backend.

Implemented:

- Harbor chat page
- Session-only message history
- Message input and submit button
- Loading and error states
- Suggested prompt buttons
- API client for `POST /api/chat`
- Citation rendering from backend responses

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
