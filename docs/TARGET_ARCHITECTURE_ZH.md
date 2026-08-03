# Harbor AI Target Architecture

Date: 2026-08-02

本文档记录 Harbor AI 之后要采用的目标架构。

Harbor AI 不应该只是一个本地 Markdown RAG demo。它的目标应该是：

```text
Official web source based semantic RAG healthcare communication system
```

也就是说，Harbor AI 应该以可信 Ontario 官方网页为主要 source input，同时保留 curated Markdown 作为 seed knowledge、fallback knowledge 和 GitHub 可读知识版本。

## 1. 核心判断

Harbor AI 的核心不是“用户问一句，AI 聊一句”，而是一个完整的 AI healthcare communication workflow。

目标系统应该包含两条主线：

```text
1. Indexing Pipeline
   把可信医疗信息处理成可检索知识索引。

2. User Query Pipeline
   根据用户问题、语音转写或 Live Assist 输入检索知识，并生成安全的沟通支持。
```

## 2. 六层架构

Harbor AI 的目标架构分为六层：

```text
1. Source Layer
2. Source Ingestion Layer
3. Document Processing Layer
4. Knowledge Index Layer
5. User Query Layer
6. Product Layer
```

## 3. Source Layer

Source Layer 是可信信息来源。

核心来源应该是 Ontario 官方或可信医疗网站：

```text
Ontario.ca
Health811
Health Care Connect
CPSO Doctor Search
College of Nurses of Ontario Registry
Ontario Health
Ontario Ministry of Health
```

当前已有 Markdown knowledge base 仍然保留，但定位调整为：

```text
curated seed knowledge
GitHub-readable source snapshot
fallback source for local development
```

也就是说：

```text
Official web pages = primary trusted source input
Markdown files = curated fallback and reviewable project source
```

## 4. Source Ingestion Layer

Source Ingestion Layer 负责把 source 加载进系统。

目标模块：

```text
source_registry.py
web_loader.py
markdown_loader.py
allowed_domains.py
```

职责：

```text
维护官方 URL 列表
限制允许抓取的 domain
加载官方网页 HTML
加载本地 Markdown
记录 source URL / retrieved_at / source type
```

重要原则：

```text
不做用户查询时的实时全网搜索。
不抓私人诊所营销页作为核心知识来源。
不把 LLM 生成内容当作 source。
```

推荐方式：

```text
official source URL list
↓
scheduled or manual ingestion
↓
indexed knowledge base
↓
query-time retrieval
```

## 5. Document Processing Layer

Document Processing Layer 负责把原始 source 变成结构化文档。

目标模块：

```text
text_extractor.py
structure_normalizer.py
toc_parser.py
semantic_chunker.py
metadata_augmenter.py
```

职责：

```text
从网页中提取正文
移除 navigation / footer / repeated UI text
保留 heading / list / source references
整理 title / sections / metadata
根据语义边界切 chunk
为 chunk 增加 category / source / province / use_case 等 metadata
```

TOC 是 Table of Contents，目录。它不是图片处理，而是帮助系统理解：

```text
H1
H2
H3
section order
```

如果单独做 TOC parser 太复杂，可以先把它合并进 `structure_normalizer.py` 或 `semantic_chunker.py`。

## 6. Semantic Chunking

Harbor AI 不应该长期停留在简单 paragraph chunking。

目标是 semantic chunking：

```text
按完整语义单元切块
保留 section heading
保留 source metadata
保留 safety context
让每个 chunk 能独立支持一个 retrieval result
```

例子：

```text
Chunk 1: What OHIP is
Chunk 2: What a health card is
Chunk 3: What to bring to a clinic
Chunk 4: How to describe symptoms
Chunk 5: When to seek emergency care
```

AI 可以参与：

```text
判断 chunk 边界
生成 chunk summary
生成 keywords
标记 use_case: prepare / live_assist
标记 safety relevance
```

## 7. Knowledge Index Layer

Knowledge Index Layer 负责把 processed chunks 变成可检索知识。

目标模块：

```text
embedding_service.py
vector_store_service.py
knowledge_index_service.py
indexing_harness.py
```

职责：

```text
调用 AI embedding model
生成 chunk embeddings
写入 Qdrant
更新已有 source 的 indexed version
提供 indexing pipeline 的运行入口
```

Qdrant 是一个 vector database。

它存：

```text
chunk text
chunk metadata
embedding vector
source information
```

Qdrant 不是两个数据库。它在两个阶段被使用：

```text
Indexing Pipeline: 写入 Qdrant
User Query Pipeline: 从 Qdrant 检索
```

## 8. User Query Layer

User Query Layer 负责处理用户输入。

目标模块：

```text
query_rewriter_service.py
rag_service.py
retriever_service.py
safety_service.py
llm_service.py
context_service.py
translation_service.py
speech_service.py
```

目标流程：

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

RAG 放在 User Query Pipeline 里，因为 RAG 是从用户问题出发：

```text
用户提出问题
↓
系统检索相关 chunks
↓
LLM 基于 retrieved chunks 生成回答
```

## 9. Product Layer

Product Layer 是用户实际看到的体验。

Harbor AI 的核心页面仍然是：

```text
Prepare
Live Assist
```

Prepare 负责：

```text
收集 visit reason
整理 symptom notes
生成 checklist
生成 questions to ask
生成 Shared Context
```

Live Assist 负责：

```text
接收 transcript / speech-to-text
使用 Shared Context
解释 clinician instructions
生成 clear English phrases
提供 multilingual communication support
总结 follow-up notes
```

## 10. 暂时不做的模块

Harbor AI 当前不需要：

```text
ACL resolver
Google OAuth
enterprise permission system
OCR PDF
image document processing
complex multi-agent workflows
```

原因：

```text
Harbor AI 是 GitHub portfolio project，不是政府企业文档系统。
当前重点是 AI healthcare communication workflow，不是权限管理或文件系统集成。
```

## 11. 后续开发顺序

推荐顺序：

```text
1. Commit current embedding scaffold and architecture docs
2. Add source registry
3. Add web_loader for official source URLs
4. Add text_extractor
5. Add structure_normalizer
6. Add semantic_chunker
7. Add metadata_augmenter
8. Upgrade embedding_service to real OpenAI embeddings
9. Add Qdrant vector_store_service
10. Add knowledge_index_service / indexing_harness
11. Add user query RAG pipeline
12. Integrate Prepare
13. Integrate Shared Context
14. Integrate Live Assist
```

## 12. 最终一句话

Harbor AI 的目标架构是：

```text
Trusted Ontario official web sources
→ AI-assisted semantic indexing
→ Qdrant vector retrieval
→ Shared Context
→ safety-aware LLM communication support
```

