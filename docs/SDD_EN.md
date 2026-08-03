# Harbor AI SDD

Version: v1.1  
Date: 2026-07-13  
Document Type: Software Design Document / Technical Execution Guide  
Audience: Beginners building an AI portfolio project from scratch  
Project Scope: Ontario newcomers, non-emergency primary care communication, Prepare + Live Assist

## 1. What You Are Building

Harbor AI should become a complete AI product project that can be published on GitHub. It does not need to be overly complex at the beginning, but it should be well structured, runnable, and easy to present.

The final project should include:

- A GitHub repository
- A clear README
- A PRD
- An SDD
- Official Ontario web-source ingestion
- A curated Markdown seed/fallback knowledge base
- A semantic knowledge indexing pipeline
- A user query pipeline for RAG retrieval and LLM response generation
- A FastAPI backend
- A React + TypeScript frontend
- A Qdrant vector database
- A Shared Context service
- A local Docker Compose setup
- A demo scenario

Core product logic:

```text
Indexing Pipeline
    trusted Ontario web sources / Markdown seed knowledge
        ↓
    extraction + structure normalization
        ↓
    semantic chunking + AI embeddings
        ↓
    Qdrant vector database

User Query Pipeline
    Prepare / Live Assist input
        ↓
    Shared Context + query rewriting
        ↓
    semantic retrieval
        ↓
    safety-aware LLM response
```

## 2. Tech Stack

### Frontend

- React
- TypeScript
- Vite

Why:

- Common for GitHub portfolio projects
- Fast to start
- Suitable for a two-page MVP
- Easy to deploy to Vercel or Netlify

### Backend

- Python
- FastAPI

Why:

- Good for AI API integration
- Good for RAG pipeline development
- Provides automatic API documentation
- Works well with LangChain, LlamaIndex, Qdrant, and the OpenAI SDK ecosystem

### AI

- OpenAI Responses API for LLM responses
- OpenAI Embeddings API for document embeddings
- OpenAI speech-to-text for transcription

### Vector Database

- Qdrant

Why:

- Friendly for local Docker usage
- Simple API
- Suitable for a portfolio demo

### Knowledge Sources

- Official Ontario web pages
- Curated Markdown seed/fallback files

Why:

- Official web pages provide trusted source material.
- Curated Markdown keeps the project readable on GitHub.
- Markdown snapshots help with local development and reproducible demos.
- Both source types can flow into the same semantic indexing pipeline.

## 3. Recommended Project Structure

Recommended repository name:

```text
harbor-ai
```

Recommended directory structure:

```text
harbor-ai/
  README.md
  .gitignore
  .env.example
  docker-compose.yml

  docs/
    PRD_ZH.md
    PRD_EN.md
    SDD_ZH.md
    SDD_EN.md
    architecture.md
    demo_script.md

  knowledge_base/
      ontario/
        primary_care/
          care_options.md
          finding_primary_care.md
        insurance/
          ohip_basics.md
        visit_preparation/
          visit_checklist.md
          symptom_communication.md
        safety/
          emergency_and_ai_limits.md

  backend/
    app/
      main.py
      config.py
      api/
        prepare.py
        live_assist.py
        health.py
      models/
        requests.py
        responses.py
        context.py
      loaders/
        markdown_loader.py
        web_loader.py
      processors/
        text_extractor.py
        structure_normalizer.py
        semantic_chunker.py
      services/
        knowledge_index_service.py
        embedding_service.py
        vector_store_service.py
        rag_service.py
        query_rewriter_service.py
        llm_service.py
        context_service.py
        safety_service.py
        speech_service.py
      prompts/
        prepare_prompt.md
        live_assist_prompt.md
        safety_prompt.md
      utils/
        text_utils.py
    scripts/
      ingest_knowledge_base.py
    tests/
      test_chunking.py
      test_context_service.py
    requirements.txt
    Dockerfile

  frontend/
    src/
      main.tsx
      App.tsx
      pages/
        PreparePage.tsx
        LiveAssistPage.tsx
      components/
        VisitBrief.tsx
        ContextPanel.tsx
        ChatPanel.tsx
        SafetyNotice.tsx
      api/
        client.ts
      types/
        visit.ts
      styles/
        global.css
    package.json
    Dockerfile
```

## 4. Step 0: Prepare Accounts and Tools

Before writing code, prepare the basic tools.

### 4.1 Create a GitHub Account

1. Open https://github.com/
2. Click Sign up.
3. Create an account.
4. Remember your username.
5. Your repository URL will look like:

```text
https://github.com/YOUR_USERNAME/harbor-ai
```

### 4.2 Install Git

Check whether Git is installed:

```bash
git --version
```

If Git is not installed:

- On macOS, install Xcode Command Line Tools or use Homebrew.
- On Windows, install Git for Windows.

Set your name and email:

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

Check the configuration:

```bash
git config --global --list
```

### 4.3 Install VS Code

1. Open https://code.visualstudio.com/
2. Download and install VS Code.
3. Recommended extensions:
   - Python
   - Pylance
   - ESLint
   - Prettier
   - Docker
   - GitHub Pull Requests

### 4.4 Install Node.js

Check whether Node.js is installed:

```bash
node --version
npm --version
```

Use an LTS version.

### 4.5 Install Python

Check Python:

```bash
python3 --version
```

Python 3.11 or 3.12 is recommended.

### 4.6 Install Docker Desktop

1. Open https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop.
3. Install and start Docker Desktop.
4. Check:

```bash
docker --version
docker compose version
```

### 4.7 Prepare an OpenAI API Key

1. Open https://platform.openai.com/
2. Log in.
3. Create an API key.
4. Do not commit the API key to GitHub.
5. Store it only in a local `.env` file.

## 5. Step 1: Create a GitHub Repository

For beginners, the easiest approach is to create the repository on GitHub first, then clone it to your computer.

### 5.1 Create the Repository on GitHub

1. Open https://github.com/
2. Log in.
3. Click the `+` button in the upper-right corner.
4. Click `New repository`.
5. Repository name:

```text
harbor-ai
```

6. Description:

```text
AI-powered healthcare communication assistant for newcomers in Ontario.
```

7. Choose `Public`.
8. Check `Add a README file`.
9. Select the Python `.gitignore` template if available.
10. Leave License empty for now, or choose MIT License later.
11. Click `Create repository`.

### 5.2 Clone the Repository Locally

On the GitHub repository page, click the green `Code` button and copy the HTTPS URL.

Choose where to store the project locally. For example:

```bash
cd ~/Documents
```

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/harbor-ai.git
cd harbor-ai
```

Check the current status:

```bash
git status
```

Open the project in VS Code:

```bash
code .
```

If `code .` does not work, open VS Code manually, then choose File -> Open Folder and select the `harbor-ai` folder.

## 6. Step 2: Create Basic Documentation

### 6.1 Create the docs Directory

```bash
mkdir docs
```

Add the existing documents:

```text
docs/PRD_ZH.md
docs/PRD_EN.md
docs/SDD_ZH.md
docs/SDD_EN.md
```

### 6.2 Update README

The README is the front page of the GitHub project.

Recommended README structure:

```md
# Harbor AI

Harbor AI is an AI-powered healthcare communication assistant for newcomers in Ontario.

## Problem

Newcomers often struggle to prepare for primary care visits and communicate clearly during healthcare interactions.

## MVP

- Prepare page
- Live Assist page
- Shared Context
- RAG over an indexed Ontario healthcare knowledge base built from official web sources and curated Markdown seed content

## Tech Stack

- React + TypeScript
- FastAPI
- OpenAI APIs
- Qdrant
- Docker Compose

## Documentation

- PRD: docs/PRD_EN.md
- SDD: docs/SDD_EN.md

## Disclaimer

Harbor AI is not a medical diagnosis tool and does not replace licensed healthcare professionals.
```

### 6.3 First Commit

Check changes:

```bash
git status
```

Add files:

```bash
git add .
```

Commit:

```bash
git commit -m "Add initial product documentation"
```

Push:

```bash
git push origin main
```

## 7. Step 3: Create the Knowledge Base

### 7.1 Create Directories

```bash
mkdir -p knowledge_base/ontario/primary_care
mkdir -p knowledge_base/ontario/insurance
mkdir -p knowledge_base/ontario/visit_preparation
mkdir -p knowledge_base/ontario/safety
```

### 7.2 Create the First Markdown Seed Sources

Start with six files:

```text
knowledge_base/ontario/primary_care/care_options.md
knowledge_base/ontario/primary_care/finding_primary_care.md
knowledge_base/ontario/insurance/ohip_basics.md
knowledge_base/ontario/visit_preparation/visit_checklist.md
knowledge_base/ontario/visit_preparation/symptom_communication.md
knowledge_base/ontario/safety/emergency_and_ai_limits.md
```

Use this template for each file:

```md
# Topic Title

## Summary

## When to use this

## What newcomers should know

## What to bring / prepare

## Common questions

## Useful phrases

## Safety notes

## Sources
- Source name: URL
```

### 7.3 Recommended Official Sources

Use Ontario-specific official or highly trusted sources:

- Ontario.ca - Health care in Ontario: https://www.ontario.ca/page/health-care-ontario
- Ontario.ca - Apply for OHIP and get a health card: https://www.ontario.ca/page/apply-ohip-and-get-health-card
- Ontario.ca - What OHIP covers: https://www.ontario.ca/page/what-ohip-covers
- Ontario.ca - Find a doctor or nurse practitioner: https://www.ontario.ca/page/find-family-doctor-or-nurse-practitioner
- Health811 Ontario: https://health811.ontario.ca/
- Health Care Connect: https://hcc3.hcc.moh.gov.on.ca/
- CPSO Find a Doctor: https://doctors.cpso.on.ca/
- College of Nurses of Ontario Registry: https://registry.cno.org/

### 7.4 Knowledge Base Principles

- Do not copy long passages directly from web pages.
- Rewrite information in your own words.
- Keep the source URL.
- Each file should focus on one topic.
- Each file should include safety notes.
- Do not write diagnosis advice.
- Treat Markdown as seed/fallback content, not the only long-term source type.
- Treat official web pages as controlled ingestion sources, not live query-time search targets.

### 7.5 Commit

```bash
git add knowledge_base
git commit -m "Add initial Ontario healthcare knowledge base"
git push origin main
```

## 8. Step 4: Create the Backend

### 8.1 Create the backend Directory

```bash
mkdir backend
cd backend
```

### 8.2 Create a Python Virtual Environment

```bash
python3 -m venv .venv
```

Activate the virtual environment:

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 8.3 Install Backend Dependencies

```bash
pip install fastapi uvicorn python-dotenv openai qdrant-client pydantic python-multipart
```

Generate `requirements.txt`:

```bash
pip freeze > requirements.txt
```

### 8.4 Create the Backend Structure

```bash
mkdir -p app/api app/models app/loaders app/processors app/services app/prompts app/utils scripts tests
touch app/main.py app/config.py
touch app/api/health.py app/api/prepare.py app/api/live_assist.py
touch app/models/requests.py app/models/responses.py app/models/context.py
touch app/loaders/markdown_loader.py app/loaders/web_loader.py
touch app/processors/text_extractor.py app/processors/structure_normalizer.py
touch app/processors/semantic_chunker.py
touch app/services/knowledge_index_service.py
touch app/services/llm_service.py app/services/embedding_service.py
touch app/services/rag_service.py app/services/vector_store_service.py
touch app/services/query_rewriter_service.py app/services/context_service.py
touch app/services/safety_service.py app/services/speech_service.py
touch app/utils/text_utils.py
touch scripts/ingest_knowledge_base.py
```

### 8.5 Add a Health Check API

`backend/app/main.py`:

```python
from fastapi import FastAPI
from app.api import health, prepare, live_assist

app = FastAPI(title="Harbor AI API")

app.include_router(health.router, prefix="/api")
app.include_router(prepare.router, prefix="/api")
app.include_router(live_assist.router, prefix="/api")
```

`backend/app/api/health.py`:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "harbor-ai-api"}
```

### 8.6 Run the Backend Locally

In the `backend/` directory:

```bash
uvicorn app.main:app --reload --port 8000
```

Open in the browser:

```text
http://localhost:8000/api/health
```

If you see:

```json
{"status":"ok","service":"harbor-ai-api"}
```

the backend is running successfully.

### 8.7 Commit

Return to the project root:

```bash
cd ..
git add backend
git commit -m "Add FastAPI backend skeleton"
git push origin main
```

## 9. Step 5: Configure Environment Variables

### 9.1 Create `.env.example`

Create this file in the project root:

```text
.env.example
```

Content:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=harbor_knowledge
```

### 9.2 Create a Local `.env`

Create:

```text
backend/.env
```

Content:

```env
OPENAI_API_KEY=your_real_api_key_here
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=harbor_knowledge
```

### 9.3 Update `.gitignore`

Create or update `.gitignore` in the project root:

```gitignore
.env
backend/.env
backend/.venv/
__pycache__/
*.pyc
node_modules/
dist/
.DS_Store
```

### 9.4 Check That API Keys Are Not Tracked

```bash
git status
```

Make sure `.env` is not listed as a file to commit.

### 9.5 Commit

```bash
git add .env.example .gitignore
git commit -m "Add environment configuration template"
git push origin main
```

## 10. Step 6: Start Qdrant

### 10.1 Create `docker-compose.yml`

Create this file in the project root:

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage

volumes:
  qdrant_storage:
```

### 10.2 Start Qdrant

```bash
docker compose up -d qdrant
```

Check:

```bash
docker ps
```

Open:

```text
http://localhost:6333/dashboard
```

If you can see the Qdrant dashboard, the vector database is running.

### 10.3 Commit

```bash
git add docker-compose.yml
git commit -m "Add Qdrant docker compose setup"
git push origin main
```

## 11. Step 7: Implement the Semantic Indexing Pipeline

The goal of the semantic indexing pipeline is:

```text
Load trusted Ontario sources
    ↓
Extract useful text
    ↓
Normalize document structure
    ↓
Create semantic chunks and metadata
    ↓
Create AI embeddings
    ↓
Store vectors in Qdrant
```

This pipeline prepares the knowledge before users ask questions. It should be separate from the user query pipeline.

### 11.1 `markdown_loader` and `web_loader`

Responsibilities:

- Read `knowledge_base/**/*.md`
- Return file path, title, content, and source metadata
- Load official Ontario web pages as primary source material for indexing
- Do not scrape websites live for every user question

### 11.2 `text_extractor`

Responsibilities:

- Extract useful body text from Markdown or web source content
- Remove navigation, footer, repeated UI text, and non-content material
- Preserve headings, lists, and source references when useful

### 11.3 `structure_normalizer`

Responsibilities:

- Convert different source formats into a common document shape
- Preserve title, sections, category, province, source path, source URL, and retrieval date
- Support official web-source ingestion

### 11.4 `semantic_chunker`

Responsibilities:

- Split content into meaning-preserving chunks
- Use headings and sections as semantic boundaries
- Keep complete healthcare communication topics together
- Add metadata such as section title, category, source, province, and use case

### 11.5 `embedding_service`

Responsibilities:

- Call the OpenAI Embeddings API for real AI embeddings
- Input chunk text
- Output vector embeddings
- Keep a mock/local embedding implementation only as a development fallback

### 11.6 `vector_store_service`

Responsibilities:

- Create or connect to the Qdrant collection
- Upsert vectors
- Search similar chunks
- Return chunk text and metadata with search results

### 11.7 `knowledge_index_service`

Responsibilities:

- Orchestrate loading, extraction, normalization, semantic chunking, embedding, and vector storage
- Act as the backend version of the indexing pipeline controller

### 11.8 `ingest_knowledge_base.py`

Responsibilities:

- Run the knowledge indexing pipeline from a script
- Run whenever official source pages, Markdown seed content, or indexed source material changes

Run:

```bash
cd backend
source .venv/bin/activate
python scripts/ingest_knowledge_base.py
```

Successful output should look like:

```text
Loaded 6 source documents
Normalized 6 documents
Created 42 semantic chunks
Embedded 42 chunks
Upserted 42 vectors into Qdrant
```

### 11.9 Commit

```bash
git add backend/app/loaders backend/app/processors backend/app/services backend/scripts
git commit -m "Add semantic indexing pipeline"
git push origin main
```

## 11A. Step 7A: Implement the User Query Pipeline

The user query pipeline runs when a user asks a Prepare question or uses Live Assist.

Target flow:

```text
User question / transcript
    ↓
Shared Context
    ↓
Query rewriting
    ↓
Query embedding
    ↓
Qdrant semantic retrieval
    ↓
Safety layer
    ↓
LLM response
```

Recommended services:

```text
query_rewriter_service.py
rag_service.py
safety_service.py
llm_service.py
context_service.py
```

RAG belongs in this user query pipeline because it starts from the user input, retrieves relevant indexed chunks, and passes those chunks to the LLM.

## 12. Step 8: Implement the Prepare API

### 12.1 Prepare API Input

Endpoint:

```text
POST /api/prepare
```

Request body:

```json
{
  "visit_type": "walk_in_clinic",
  "preferred_language": "Chinese",
  "symptoms": "stomach pain for three days",
  "duration": "3 days",
  "severity": "moderate",
  "concerns": "I am worried I may need tests"
}
```

### 12.2 Prepare API Output

Response body:

```json
{
  "visit_context_id": "ctx_123",
  "visit_brief": {
    "summary": "The user has had stomach pain for three days...",
    "what_to_bring": ["Health card if available", "Medication list"],
    "likely_questions": ["When did the pain start?", "Where is the pain located?"],
    "questions_to_ask": ["Do I need any tests?", "What symptoms should I watch for?"],
    "useful_phrases": ["I have had stomach pain for three days."]
  },
  "safety_notice": "This is not medical advice. If symptoms are severe or urgent, seek immediate care."
}
```

### 12.3 Internal Prepare Flow

```text
Receive user input
    ↓
Retrieve relevant chunks from Qdrant
    ↓
Build prompt with retrieved knowledge + user input
    ↓
Call LLM
    ↓
Generate visit brief
    ↓
Store Shared Context
    ↓
Return visit_context_id + visit_brief
```

### 12.4 Shared Context Storage

For the MVP, use in-memory storage first.

Example:

```python
CONTEXT_STORE = {}
```

Later, this can be upgraded to SQLite, PostgreSQL, or Redis.

### 12.5 Commit

```bash
git add backend
git commit -m "Add Prepare API with shared context"
git push origin main
```

## 13. Step 9: Implement the Live Assist API

### 13.1 Live Assist API Input

Endpoint:

```text
POST /api/live-assist
```

Request body:

```json
{
  "visit_context_id": "ctx_123",
  "user_message": "I want to ask if I need a test",
  "mode": "rewrite"
}
```

### 13.2 Live Assist API Output

Response body:

```json
{
  "response_type": "communication_support",
  "suggested_phrase": "Could you let me know whether I need any tests based on my symptoms?",
  "plain_language_explanation": "This is a polite way to ask whether the doctor recommends tests.",
  "safety_notice": "This is communication support, not medical advice."
}
```

### 13.3 Internal Live Assist Flow

```text
Receive user message
    ↓
Load Shared Context by visit_context_id
    ↓
Optionally retrieve RAG chunks
    ↓
Build Live Assist prompt
    ↓
Call LLM
    ↓
Return suggested wording / explanation / translation
```

### 13.4 Live Assist Modes

The MVP can support four modes:

```text
rewrite
explain
translate
summarize
```

Meaning:

- `rewrite`: rewrite what the user wants to say into clear English
- `explain`: explain what the doctor or clinic staff said in plain language
- `translate`: provide a short translation
- `summarize`: summarize visit takeaways

### 13.5 Multilingual Live Assist Design

Live Assist should be designed with multilingual support from the beginning, even if the first version only supports English + Chinese.

Recommended language fields:

```json
{
  "visit_context_id": "ctx_123",
  "user_message": "I want to ask if I need a test",
  "mode": "rewrite",
  "source_language": "en",
  "target_language": "zh",
  "language_direction": "en_to_zh"
}
```

Possible language directions:

```text
en_to_user_language
user_language_to_en
auto
```

Frontend UI can include:

- Source language selector
- Target language selector
- Auto-detect toggle
- Original caption
- Translated caption
- Suggested phrases panel

The backend can keep recent conversation history:

```json
[
  {
    "source_language": "en",
    "target_language": "zh",
    "source_text": "Do you have a fever?",
    "target_text": "你发烧了吗？"
  }
]
```

This history can be used to generate three next-phrase suggestions:

```json
{
  "suggestions": [
    {
      "english": "Could you explain that more slowly?",
      "preferred_language": "你可以说慢一点吗？"
    }
  ]
}
```

Design notes:

- Multilingual support should serve healthcare communication, not become a general translator.
- The MVP can start with text input, translation, and suggested phrases.
- Speech-to-text can later reuse the same language direction logic.
- For low-resource languages or phonetic / romanized input, speech recognition can first produce approximate text, then the LLM can interpret the meaning.
- All translations should keep safety notices and avoid being treated as medical advice.

### 13.6 Commit

```bash
git add backend
git commit -m "Add Live Assist API"
git push origin main
```

## 14. Step 10: Implement Speech-to-Text

Keep speech simple for the MVP.

Endpoint:

```text
POST /api/transcribe
```

Input:

- audio file

Output:

```json
{
  "text": "I have had stomach pain for three days."
}
```

Do not start with real-time streaming. The first version can use audio upload or browser recording, then submit the audio to the backend.

Recommended order:

1. Complete the text input version first.
2. Add speech-to-text.
3. Consider real-time speech later.

Commit:

```bash
git add backend
git commit -m "Add basic speech transcription endpoint"
git push origin main
```

## 15. Step 11: Create the Frontend

### 15.1 Create a React App

In the project root:

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

Start the frontend:

```bash
npm run dev
```

Open:

```text
http://localhost:5173
```

### 15.2 Frontend Pages

Only two pages are required:

```text
/prepare
/live-assist
```

You can also avoid routing in the first version and switch pages with simple React state.

### 15.3 Prepare Page UI

The Prepare page should include:

- Visit type selector
- Preferred language selector
- Symptoms textarea
- Duration input
- Severity selector
- Concerns textarea
- Generate Visit Brief button
- Visit Brief result panel

### 15.4 Live Assist Page UI

The Live Assist page should include:

- Visit Context summary panel
- Mode selector
- User message textarea
- Send button
- AI response panel
- Safety notice

### 15.5 Frontend API Client

`frontend/src/api/client.ts` calls the backend:

```ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
```

Add this to `.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 15.6 Commit

```bash
git add frontend
git commit -m "Add React frontend skeleton"
git push origin main
```

## 16. Step 12: Connect Frontend and Backend

### 16.1 Start Qdrant

```bash
docker compose up -d qdrant
```

### 16.2 Start Backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 16.3 Start Frontend

Open a new terminal:

```bash
cd frontend
npm run dev
```

### 16.4 Test the Prepare Flow

1. Open `http://localhost:5173`
2. Go to the Prepare page.
3. Select `walk-in clinic`.
4. Enter symptoms.
5. Click Generate.
6. Check whether a visit brief is generated.
7. Check whether `visit_context_id` is returned.

### 16.5 Test the Live Assist Flow

1. Go to the Live Assist page.
2. Confirm that the page can read the previous context.
3. Enter:

```text
I want to ask if I need a test.
```

4. Check whether it returns a clearer English phrase.

## 17. Step 13: Run the Full Project with Docker Compose

In the second phase, add backend and frontend to Docker.

Final `docker-compose.yml` can include:

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage

  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      - qdrant

  frontend:
    build:
      context: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend

volumes:
  qdrant_storage:
```

Run:

```bash
docker compose up --build
```

## 18. Step 14: Testing

### 18.1 Backend Tests

Write at least these tests:

- Markdown loader can read seed/fallback files
- Web loader can ingest allowed official source pages
- Chunker can split text into chunks
- Context service can save and retrieve context
- Prepare API returns `visit_context_id`
- Live Assist API returns an error when context is missing

Run:

```bash
cd backend
pytest
```

Install test dependencies:

```bash
pip install pytest httpx
pip freeze > requirements.txt
```

### 18.2 Manual Test Checklist

Before each major commit, check:

- Qdrant starts successfully
- Backend `/api/health` works
- Prepare page generates a result
- Live Assist reuses context
- `.env` is not committed to GitHub
- README setup steps are still correct

## 19. Step 15: Git Workflow

### 19.1 Daily Development Flow

Before starting work:

```bash
git status
git pull origin main
```

Create a branch:

```bash
git checkout -b feature/prepare-api
```

After development:

```bash
git status
git add .
git commit -m "Add Prepare API"
git push origin feature/prepare-api
```

Then create a Pull Request on GitHub.

### 19.2 Pull Request

PR title example:

```text
Add Prepare API
```

PR description example:

```md
## Summary

- Added Prepare API endpoint
- Added visit context generation
- Connected RAG retrieval to visit brief generation

## Test

- Ran backend locally
- Tested /api/prepare with sample walk-in clinic input
```

After merging the PR:

```bash
git checkout main
git pull origin main
```

### 19.3 Commit Message Style

Recommended:

```text
Add initial knowledge base
Add FastAPI backend skeleton
Add Qdrant ingestion pipeline
Add Prepare API
Add Live Assist UI
Fix context retrieval error
Update README setup guide
```

Avoid:

```text
update
fix
final
try again
```

## 20. Step 16: Polish the GitHub Presentation

The GitHub repository should be understandable at first glance.

### 20.1 README Must Include

- Product description
- Problem statement
- MVP scope
- Demo flow
- Architecture diagram
- Tech stack
- Local setup
- Environment variables
- How to run
- Screenshots
- Disclaimer
- Documentation links

### 20.2 Recommended README Architecture Diagram

```text
Indexing Pipeline
Trusted Ontario web sources / Markdown seed knowledge
    ↓
Loader + Extractor + Structure Normalizer
    ↓
Semantic Chunker + AI Embeddings
    ↓
Qdrant Vector DB

User Query Pipeline
React Frontend
    ↓
FastAPI Backend
    ↓
Shared Context + Query Rewriter
    ↓
Semantic RAG Retriever
    ↓
Safety Layer
    ↓
LLM Response
```

### 20.3 Recommended Screenshots

Create:

```text
docs/screenshots/
```

Add:

```text
prepare-page.png
live-assist-page.png
architecture.png
```

### 20.4 Demo Script

Create:

```text
docs/demo_script.md
```

Content:

```md
# Demo Script

## Scenario

An international student in Ontario has had stomach pain for three days and wants to visit a walk-in clinic.

## Step 1: Prepare

The user enters symptoms and selects walk-in clinic.

## Step 2: Visit Brief

Harbor AI generates a checklist, likely questions, useful phrases, and a visit context.

## Step 3: Live Assist

The user asks how to say: "I want to ask if I need a test."

## Step 4: AI Response

Harbor AI suggests a clear English phrase and explains it in plain language.
```

## 21. Step 17: MVP Development Order

Do not build everything at once. Recommended order:

1. GitHub repo + README
2. PRD + SDD
3. Knowledge source registry and Markdown seed files
4. Backend skeleton
5. Markdown loader and web source plan
6. Mock embedding scaffold
7. Semantic indexing service
8. Semantic chunking and metadata augmentation
9. OpenAI embeddings
10. Qdrant Docker
11. Qdrant ingestion
12. User query pipeline
13. RAG search endpoint
14. Prepare API
15. Shared Context
16. Live Assist API
17. Frontend Prepare page
18. Frontend Live Assist page
19. Basic styling
20. Speech-to-text
21. Docker Compose
22. Tests
23. README polish
24. Screenshots
25. Demo script

## 22. Step 18: What Not to Build in Version 1

Do not build these in the first version:

- User login
- Complex permission system
- Long-term personal medical record storage
- Mobile app
- Real-time video recognition
- Insurance claims
- Automatic appointment booking
- Complex multi-agent workflows
- MCP
- Specialist care
- Emergency triage

Why:

- These features would make the project scope too large.
- A GitHub portfolio project should clearly communicate the core product logic.
- The MVP highlight should be Prepare + Shared Context + Live Assist + RAG.

## 23. Minimum Deliverable Version

The fastest presentable version should include:

- Complete README
- Complete PRD / SDD
- Six Markdown seed knowledge files
- Source registry for official web pages
- Qdrant can start
- Semantic indexing pipeline can store chunks in Qdrant
- User query pipeline can retrieve relevant chunks
- Prepare API can return a visit brief
- Live Assist API can reuse `visit_context_id`
- React has two pages
- One complete demo scenario

This is already enough for a GitHub portfolio demo.

## 24. Recommended Milestones

### Milestone 1: Project Setup

Goal:

- GitHub repo created
- README draft completed
- PRD / SDD added to docs
- Basic directory structure created

### Milestone 2: Knowledge Base + RAG

Goal:

- Markdown seed sources completed
- Official web source registry started
- Semantic chunking completed
- AI embedding service completed
- Qdrant ingestion completed
- User query pipeline retrieves relevant chunks
- RAG search works with metadata and source references

### Milestone 3: Backend MVP

Goal:

- Prepare API completed
- Live Assist API completed
- Shared Context completed
- Safety notice completed

### Milestone 4: Frontend MVP

Goal:

- Prepare page completed
- Live Assist page completed
- Frontend and backend integration completed

### Milestone 5: Portfolio Polish

Goal:

- README completed
- Screenshots completed
- Demo script completed
- Docker Compose works
- GitHub repo looks professional

## 25. Official References

GitHub:

- GitHub Docs - Quickstart for repositories: https://docs.github.com/en/repositories/creating-and-managing-repositories/quickstart-for-repositories
- GitHub Docs - Adding locally hosted code to GitHub: https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github

OpenAI:

- OpenAI API docs: https://developers.openai.com/api/docs/
- Text generation guide: https://developers.openai.com/api/docs/guides/text
- Embeddings guide: https://developers.openai.com/api/docs/guides/embeddings
- Speech-to-text guide: https://developers.openai.com/api/docs/guides/speech-to-text

Qdrant:

- Qdrant Quickstart: https://qdrant.tech/documentation/quickstart/

Docker:

- Docker Desktop: https://www.docker.com/products/docker-desktop/

## 26. One-Sentence Summary

The technical implementation path for Harbor AI should be:

> First build a trusted Ontario knowledge index with semantic chunking, AI embeddings, and Qdrant, then implement the user query pipeline for RAG, safety-aware LLM responses, Prepare, Live Assist, and Shared Context.
