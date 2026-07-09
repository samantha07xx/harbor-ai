# Harbor AI SDD

版本：v1.0  
日期：2026-07-09  
文档类型：Software Design Document / Technical Execution Guide  
适合读者：从零开始做 GitHub AI Portfolio 项目的初学者  
项目范围：Ontario newcomers, non-emergency primary care communication, Prepare + Live Assist

## 1. 你最终要做出来什么

Harbor AI 最终应该是一个可以放到 GitHub 的完整 AI 产品项目。它不需要一开始非常复杂，但需要结构专业、能跑、能展示。

最终项目应该包含：

- 一个 GitHub repository
- 一个清楚的 README
- 一份 BRD / PRD
- 一份 SDD
- 一个 Markdown knowledge base
- 一个 RAG ingestion pipeline
- 一个 FastAPI backend
- 一个 React + TypeScript frontend
- 一个 Qdrant vector database
- 一个 Shared Context service
- 一个 Docker Compose 本地运行方案
- 一个 demo scenario

核心产品逻辑：

```text
Prepare Page
    ↓
User Input + RAG Retrieval
    ↓
Visit Context
    ↓
Live Assist Page
    ↓
Context-aware Communication Support
```

## 2. 技术栈选择

### Frontend

- React
- TypeScript
- Vite

原因：

- GitHub portfolio 项目常见
- 启动快
- 适合做两个页面的 MVP
- 容易部署到 Vercel 或 Netlify

### Backend

- Python
- FastAPI

原因：

- 适合 AI API 调用
- 适合写 RAG pipeline
- 文档自动生成
- 和 LangChain / LlamaIndex / Qdrant / OpenAI SDK 生态兼容

### AI

- OpenAI Responses API for LLM responses
- OpenAI Embeddings API for document embeddings
- OpenAI speech-to-text for transcription

### Vector Database

- Qdrant

原因：

- 对本地 Docker 友好
- API 简单
- 适合 portfolio demo

### Knowledge Base

- Markdown files

原因：

- GitHub 可读
- 容易 review
- 容易 chunk
- 适合展示 RAG source quality

## 3. 推荐项目结构

建议 repository 名字：

```text
harbor-ai
```

推荐目录：

```text
harbor-ai/
  README.md
  .gitignore
  .env.example
  docker-compose.yml

  docs/
    BRD_ZH.md
    BRD_EN.md
    SDD_ZH.md
    architecture.md
    demo_script.md

  knowledge_base/
    ontario/
      primary_care/
        walk_in_clinic.md
        family_doctor.md
        nurse_practitioner.md
        health811.md
      insurance/
        ohip_basics.md
        without_ohip.md
      visit_preparation/
        appointment_checklist.md
        symptoms_description.md
        questions_to_ask.md
        after_visit_instructions.md
      safety/
        emergency_vs_primary_care.md
        when_to_call_911.md

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
      services/
        llm_service.py
        embedding_service.py
        rag_service.py
        qdrant_service.py
        context_service.py
        speech_service.py
      prompts/
        prepare_prompt.md
        live_assist_prompt.md
        safety_prompt.md
      utils/
        markdown_loader.py
        text_chunker.py
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

## 4. 第 0 步：准备账号和工具

你需要先准备这些东西。

### 4.1 创建 GitHub 账号

1. 打开 https://github.com/
2. 点击 Sign up。
3. 注册一个账号。
4. 记住你的 username。
5. 后面 GitHub repository URL 会类似：

```text
https://github.com/YOUR_USERNAME/harbor-ai
```

### 4.2 安装 Git

检查电脑是否已经有 Git：

```bash
git --version
```

如果没有安装：

- macOS 可以安装 Xcode Command Line Tools，或使用 Homebrew。
- Windows 可以安装 Git for Windows。

安装后设置你的名字和邮箱：

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

检查设置是否成功：

```bash
git config --global --list
```

### 4.3 安装 VS Code

1. 打开 https://code.visualstudio.com/
2. 下载并安装 VS Code。
3. 推荐安装 extensions：
   - Python
   - Pylance
   - ESLint
   - Prettier
   - Docker
   - GitHub Pull Requests

### 4.4 安装 Node.js

检查是否已有 Node.js：

```bash
node --version
npm --version
```

建议安装 LTS 版本。

### 4.5 安装 Python

检查 Python：

```bash
python3 --version
```

建议使用 Python 3.11 或 3.12。

### 4.6 安装 Docker Desktop

1. 打开 https://www.docker.com/products/docker-desktop/
2. 下载 Docker Desktop。
3. 安装后启动。
4. 检查：

```bash
docker --version
docker compose version
```

### 4.7 准备 OpenAI API Key

1. 打开 https://platform.openai.com/
2. 登录账号。
3. 创建 API key。
4. 不要把 API key 写进 GitHub。
5. 后面只放在本地 `.env` 文件里。

## 5. 第 1 步：创建 GitHub Repository

推荐先在 GitHub 网站创建 repository，再 clone 到本地。这样对初学者最直观。

### 5.1 在 GitHub 创建 repo

1. 打开 https://github.com/
2. 登录。
3. 右上角点击 `+`。
4. 点击 `New repository`。
5. Repository name 填：

```text
harbor-ai
```

6. Description 填：

```text
AI-powered healthcare communication assistant for newcomers in Ontario.
```

7. 选择 `Public`。
8. 勾选 `Add a README file`。
9. `.gitignore` 可以先不选，后面我们自己写。
10. License 可以选择 `MIT License`，也可以先不选。
11. 点击 `Create repository`。

### 5.2 把 repo clone 到本地

在 GitHub repo 页面点击绿色 `Code` 按钮，复制 HTTPS URL。

在电脑终端中选择一个放项目的地方：

```bash
mkdir -p ~/Projects
cd ~/Projects
```

clone：

```bash
git clone https://github.com/YOUR_USERNAME/harbor-ai.git
cd harbor-ai
```

检查当前状态：

```bash
git status
```

打开 VS Code：

```bash
code .
```

如果 `code .` 不工作，可以直接打开 VS Code，然后 File -> Open Folder，选择 `harbor-ai` 文件夹。

## 6. 第 2 步：建立基础文档

### 6.1 创建 docs 目录

```bash
mkdir docs
```

把已有 BRD 放进去：

```text
docs/BRD_ZH.md
docs/BRD_EN.md
docs/SDD_ZH.md
```

### 6.2 更新 README

README 应该是 GitHub 项目的门面。

建议 README 结构：

```md
# Harbor AI

Harbor AI is an AI-powered healthcare communication assistant for newcomers in Ontario.

## Problem

Newcomers often struggle to prepare for primary care visits and communicate clearly during healthcare interactions.

## MVP

- Prepare page
- Live Assist page
- Shared Context
- RAG over curated Ontario healthcare Markdown knowledge base

## Tech Stack

- React + TypeScript
- FastAPI
- OpenAI APIs
- Qdrant
- Docker Compose

## Documentation

- BRD: docs/BRD_EN.md
- SDD: docs/SDD_ZH.md

## Disclaimer

Harbor AI is not a medical diagnosis tool and does not replace licensed healthcare professionals.
```

### 6.3 第一次 commit

查看变化：

```bash
git status
```

添加文件：

```bash
git add .
```

提交：

```bash
git commit -m "Add initial product documentation"
```

推送：

```bash
git push origin main
```

## 7. 第 3 步：建立 Knowledge Base

### 7.1 创建目录

```bash
mkdir -p knowledge_base/ontario/primary_care
mkdir -p knowledge_base/ontario/insurance
mkdir -p knowledge_base/ontario/visit_preparation
mkdir -p knowledge_base/ontario/safety
```

### 7.2 创建第一批 Markdown source

先只做 6 个文件就够：

```text
knowledge_base/ontario/primary_care/walk_in_clinic.md
knowledge_base/ontario/primary_care/family_doctor.md
knowledge_base/ontario/primary_care/nurse_practitioner.md
knowledge_base/ontario/primary_care/health811.md
knowledge_base/ontario/insurance/ohip_basics.md
knowledge_base/ontario/safety/emergency_vs_primary_care.md
```

每个文件都用这个模板：

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

### 7.3 推荐官方来源

只使用 Ontario 相关官方或高度可信来源：

- Ontario.ca - Health care in Ontario: https://www.ontario.ca/page/health-care-ontario
- Ontario.ca - Apply for OHIP and get a health card: https://www.ontario.ca/page/apply-ohip-and-get-health-card
- Ontario.ca - What OHIP covers: https://www.ontario.ca/page/what-ohip-covers
- Ontario.ca - Find a doctor or nurse practitioner: https://www.ontario.ca/page/find-family-doctor-or-nurse-practitioner
- Health811 Ontario: https://health811.ontario.ca/
- Health Care Connect: https://hcc3.hcc.moh.gov.on.ca/
- CPSO Find a Doctor: https://doctors.cpso.on.ca/
- College of Nurses of Ontario Registry: https://registry.cno.org/

### 7.4 知识库原则

- 不直接复制大段网页文字。
- 用自己的话整理。
- 保留 source URL。
- 每个文件只讲一个主题。
- 每个文件都加 Safety notes。
- 不写诊断建议。

### 7.5 commit

```bash
git add knowledge_base
git commit -m "Add initial Ontario healthcare knowledge base"
git push origin main
```

## 8. 第 4 步：建立 Backend

### 8.1 创建 backend 目录

```bash
mkdir backend
cd backend
```

### 8.2 创建 Python virtual environment

```bash
python3 -m venv .venv
```

启动 virtual environment：

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 8.3 安装后端依赖

```bash
pip install fastapi uvicorn python-dotenv openai qdrant-client pydantic python-multipart
```

生成 requirements：

```bash
pip freeze > requirements.txt
```

### 8.4 创建后端目录结构

```bash
mkdir -p app/api app/models app/services app/prompts app/utils scripts tests
touch app/main.py app/config.py
touch app/api/health.py app/api/prepare.py app/api/live_assist.py
touch app/models/requests.py app/models/responses.py app/models/context.py
touch app/services/llm_service.py app/services/embedding_service.py
touch app/services/rag_service.py app/services/qdrant_service.py
touch app/services/context_service.py app/services/speech_service.py
touch app/utils/markdown_loader.py app/utils/text_chunker.py
touch scripts/ingest_knowledge_base.py
```

### 8.5 建立健康检查 API

`backend/app/main.py`：

```python
from fastapi import FastAPI
from app.api import health, prepare, live_assist

app = FastAPI(title="Harbor AI API")

app.include_router(health.router, prefix="/api")
app.include_router(prepare.router, prefix="/api")
app.include_router(live_assist.router, prefix="/api")
```

`backend/app/api/health.py`：

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "harbor-ai-api"}
```

### 8.6 本地运行后端

在 `backend/` 目录：

```bash
uvicorn app.main:app --reload --port 8000
```

打开浏览器：

```text
http://localhost:8000/api/health
```

如果看到：

```json
{"status":"ok","service":"harbor-ai-api"}
```

说明后端启动成功。

### 8.7 commit

回到项目根目录：

```bash
cd ..
git add backend
git commit -m "Add FastAPI backend skeleton"
git push origin main
```

## 9. 第 5 步：配置环境变量

### 9.1 创建 .env.example

在项目根目录创建：

```text
.env.example
```

内容：

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=harbor_knowledge
```

### 9.2 创建本地 .env

创建：

```text
backend/.env
```

内容：

```env
OPENAI_API_KEY=你的真实 API key
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=harbor_knowledge
```

### 9.3 创建 .gitignore

项目根目录创建 `.gitignore`：

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

### 9.4 检查 API key 没有被 Git 追踪

```bash
git status
```

确认 `.env` 没有出现在将要 commit 的文件列表里。

### 9.5 commit

```bash
git add .env.example .gitignore
git commit -m "Add environment configuration template"
git push origin main
```

## 10. 第 6 步：启动 Qdrant

### 10.1 创建 docker-compose.yml

在项目根目录创建：

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

### 10.2 启动 Qdrant

```bash
docker compose up -d qdrant
```

检查：

```bash
docker ps
```

打开：

```text
http://localhost:6333/dashboard
```

如果能看到 Qdrant dashboard，说明 vector database 成功运行。

### 10.3 commit

```bash
git add docker-compose.yml
git commit -m "Add Qdrant docker compose setup"
git push origin main
```

## 11. 第 7 步：实现 RAG Ingestion

RAG ingestion 的目标是：

```text
Read Markdown
    ↓
Split into chunks
    ↓
Create embeddings
    ↓
Store vectors in Qdrant
```

### 11.1 markdown_loader

职责：

- 读取 `knowledge_base/**/*.md`
- 返回每个文件的 path、title、content、source metadata

### 11.2 text_chunker

职责：

- 把长 Markdown 切成小段
- 每段建议 500 到 900 tokens
- 保留 metadata，例如 file path、topic、section title

### 11.3 embedding_service

职责：

- 调用 OpenAI Embeddings API
- 输入 chunk text
- 输出 vector

### 11.4 qdrant_service

职责：

- 创建 collection
- upsert vectors
- search similar chunks

### 11.5 ingest_knowledge_base.py

职责：

- 串起来整个 ingestion pipeline
- 每次更新 Markdown 后运行一次

运行方式：

```bash
cd backend
source .venv/bin/activate
python scripts/ingest_knowledge_base.py
```

成功后应该打印类似：

```text
Loaded 6 markdown files
Created 42 chunks
Embedded 42 chunks
Upserted 42 vectors into Qdrant
```

### 11.6 commit

```bash
git add backend/app/services backend/app/utils backend/scripts
git commit -m "Add RAG ingestion pipeline"
git push origin main
```

## 12. 第 8 步：实现 Prepare API

### 12.1 Prepare API 输入

Endpoint：

```text
POST /api/prepare
```

Request body：

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

### 12.2 Prepare API 输出

Response body：

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

### 12.3 Prepare 内部流程

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

### 12.4 Shared Context 存储

MVP 可以先用内存存储。

例如：

```python
CONTEXT_STORE = {}
```

之后再升级到 SQLite、PostgreSQL 或 Redis。

### 12.5 commit

```bash
git add backend
git commit -m "Add Prepare API with shared context"
git push origin main
```

## 13. 第 9 步：实现 Live Assist API

### 13.1 Live Assist API 输入

Endpoint：

```text
POST /api/live-assist
```

Request body：

```json
{
  "visit_context_id": "ctx_123",
  "user_message": "I want to ask if I need a test",
  "mode": "rewrite"
}
```

### 13.2 Live Assist API 输出

Response body：

```json
{
  "response_type": "communication_support",
  "suggested_phrase": "Could you let me know whether I need any tests based on my symptoms?",
  "plain_language_explanation": "This is a polite way to ask whether the doctor recommends tests.",
  "safety_notice": "This is communication support, not medical advice."
}
```

### 13.3 Live Assist 内部流程

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

### 13.4 Live Assist modes

MVP 可以支持 4 种 mode：

```text
rewrite
explain
translate
summarize
```

含义：

- `rewrite`: 把用户想说的话改成清楚英文
- `explain`: 用简单语言解释医生或工作人员的话
- `translate`: 简短翻译
- `summarize`: 总结 visit takeaways

### 13.5 commit

```bash
git add backend
git commit -m "Add Live Assist API"
git push origin main
```

## 14. 第 10 步：实现 Speech-to-Text

MVP 可以把 speech 做得简单一点。

Endpoint：

```text
POST /api/transcribe
```

输入：

- audio file

输出：

```json
{
  "text": "I have had stomach pain for three days."
}
```

先不要做实时语音流。第一版只做上传音频文件或浏览器录音后提交。

推荐顺序：

1. 先完成文字输入版本。
2. 再加 speech-to-text。
3. 最后再考虑实时语音。

commit：

```bash
git add backend
git commit -m "Add basic speech transcription endpoint"
git push origin main
```

## 15. 第 11 步：建立 Frontend

### 15.1 创建 React app

在项目根目录：

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

启动：

```bash
npm run dev
```

打开：

```text
http://localhost:5173
```

### 15.2 前端页面

只做两个页面：

```text
/prepare
/live-assist
```

也可以先不引入 router，用简单 state 切换页面。

### 15.3 Prepare Page UI

Prepare 页面需要：

- Visit type selector
- Preferred language selector
- Symptoms textarea
- Duration input
- Severity selector
- Concerns textarea
- Generate Visit Brief button
- Visit Brief result panel

### 15.4 Live Assist Page UI

Live Assist 页面需要：

- Visit Context summary panel
- Mode selector
- User message textarea
- Send button
- AI response panel
- Safety notice

### 15.5 frontend api client

`frontend/src/api/client.ts` 负责调用后端：

```ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
```

`.env.example` 里加：

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 15.6 commit

```bash
git add frontend
git commit -m "Add React frontend skeleton"
git push origin main
```

## 16. 第 12 步：前后端联调

### 16.1 启动 Qdrant

```bash
docker compose up -d qdrant
```

### 16.2 启动 backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 16.3 启动 frontend

新开一个 terminal：

```bash
cd frontend
npm run dev
```

### 16.4 测试 Prepare flow

1. 打开 `http://localhost:5173`
2. 进入 Prepare 页面。
3. 选择 `walk-in clinic`。
4. 输入症状。
5. 点击 Generate。
6. 检查是否生成 visit brief。
7. 检查是否返回 `visit_context_id`。

### 16.5 测试 Live Assist flow

1. 进入 Live Assist 页面。
2. 确认页面能读取刚才的 context。
3. 输入：

```text
I want to ask if I need a test.
```

4. 检查是否返回更清楚的英文表达。

## 17. 第 13 步：Docker Compose 全项目运行

第二阶段可以把 backend 和 frontend 也加入 Docker。

最终 `docker-compose.yml` 可以包含：

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

运行：

```bash
docker compose up --build
```

## 18. 第 14 步：测试

### 18.1 后端测试

至少写这些测试：

- Markdown loader 是否能读文件
- Chunker 是否能切 chunk
- Context service 是否能保存和读取 context
- Prepare API 是否返回 visit_context_id
- Live Assist API 缺少 context 时是否返回错误

运行：

```bash
cd backend
pytest
```

需要安装：

```bash
pip install pytest httpx
pip freeze > requirements.txt
```

### 18.2 手动测试清单

每次提交前检查：

- Qdrant 能启动
- Backend `/api/health` 正常
- Prepare 页面能生成结果
- Live Assist 能复用 context
- 没有把 `.env` 提交到 GitHub
- README 的运行步骤仍然正确

## 19. 第 15 步：Git 工作流

### 19.1 日常开发流程

每次开始开发：

```bash
git status
git pull origin main
```

创建分支：

```bash
git checkout -b feature/prepare-api
```

开发完成后：

```bash
git status
git add .
git commit -m "Add Prepare API"
git push origin feature/prepare-api
```

然后去 GitHub 创建 Pull Request。

### 19.2 Pull Request

PR 标题示例：

```text
Add Prepare API
```

PR description 示例：

```md
## Summary

- Added Prepare API endpoint
- Added visit context generation
- Connected RAG retrieval to visit brief generation

## Test

- Ran backend locally
- Tested /api/prepare with sample walk-in clinic input
```

合并 PR 后：

```bash
git checkout main
git pull origin main
```

### 19.3 Commit message 习惯

推荐：

```text
Add initial knowledge base
Add FastAPI backend skeleton
Add Qdrant ingestion pipeline
Add Prepare API
Add Live Assist UI
Fix context retrieval error
Update README setup guide
```

避免：

```text
update
fix
final
try again
```

## 20. 第 16 步：GitHub 展示整理

GitHub repo 最后要让别人一打开就看懂。

### 20.1 README 必须包含

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

### 20.2 推荐 README architecture diagram

```text
React Frontend
    ↓
FastAPI Backend
    ↓
Context Service
    ↓
RAG Service
    ↓
Qdrant Vector DB
    ↓
Markdown Knowledge Base

FastAPI Backend
    ↓
OpenAI APIs
```

### 20.3 推荐 screenshots

创建：

```text
docs/screenshots/
```

放：

```text
prepare-page.png
live-assist-page.png
architecture.png
```

### 20.4 Demo script

创建：

```text
docs/demo_script.md
```

内容：

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

## 21. 第 17 步：MVP 开发顺序

不要一开始同时做所有功能。推荐顺序：

1. GitHub repo + README
2. BRD + SDD
3. Knowledge base Markdown
4. Backend skeleton
5. Qdrant Docker
6. Markdown loader
7. Chunking
8. Embeddings
9. Qdrant ingestion
10. RAG search endpoint
11. Prepare API
12. Shared Context
13. Live Assist API
14. Frontend Prepare page
15. Frontend Live Assist page
16. Basic styling
17. Speech-to-text
18. Docker Compose
19. Tests
20. README polish
21. Screenshots
22. Demo script

## 22. 第 18 步：第一版先不要做什么

第一版不要做：

- 用户登录
- 复杂权限系统
- 真正保存长期医疗记录
- 手机 App
- 实时视频识别
- 保险理赔
- 自动预约
- 复杂 multi-agent
- MCP
- Specialist care
- Emergency triage

原因：

- 这些会让项目范围失控。
- GitHub portfolio 项目最重要的是讲清楚核心逻辑。
- MVP 的亮点应该是 Prepare + Shared Context + Live Assist + RAG。

## 23. 最小可交付版本

如果你想最快做出可以展示的版本，最低要求是：

- README 完整
- BRD / SDD 完整
- 6 个 Markdown knowledge source
- Qdrant 能启动
- Ingestion script 能把 Markdown 存入 Qdrant
- Prepare API 能返回 visit brief
- Live Assist API 能复用 visit_context_id
- React 有两个页面
- 有一个完整 demo scenario

这个版本就已经可以放 GitHub 展示。

## 24. 推荐里程碑

### Milestone 1: Project Setup

目标：

- GitHub repo 创建完成
- README 初版完成
- BRD / SDD 放入 docs
- 基础目录结构完成

### Milestone 2: Knowledge Base + RAG

目标：

- Markdown source 完成
- Chunking 完成
- Embedding 完成
- Qdrant ingestion 完成
- RAG search 可用

### Milestone 3: Backend MVP

目标：

- Prepare API 完成
- Live Assist API 完成
- Shared Context 完成
- Safety notice 完成

### Milestone 4: Frontend MVP

目标：

- Prepare page 完成
- Live Assist page 完成
- 前后端联调完成

### Milestone 5: Portfolio Polish

目标：

- README 完整
- Screenshots 完整
- Demo script 完整
- Docker Compose 可运行
- GitHub repo 看起来专业

## 25. 官方参考链接

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

## 26. 一句话总结

Harbor AI 的技术实现路线应该是：

> 先用 Markdown 建可信知识库，再用 embeddings 和 Qdrant 做 RAG，然后用 FastAPI 提供 Prepare 和 Live Assist API，最后用 React 做两个页面，把 Prepare 生成的 Shared Context 传到 Live Assist 复用。

