# Harbor Frontend

Frontend: React, TypeScript, and Vite.

Current status: minimal Step 3 chat shell.

Implemented:

- Harbor chat page
- Session-only message history
- Message input and submit button
- Loading and error states
- Suggested prompt buttons
- API client for `POST /api/chat`

Not implemented yet:

- Real grounded RAG responses
- Citation rendering from indexed sources
- Conversation persistence
- User accounts

Run locally from this folder:

```bash
npm install
npm run dev
```

The backend should be running at `http://127.0.0.1:8000`.
