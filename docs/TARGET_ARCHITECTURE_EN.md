# Harbor AI Target Architecture

Date: 2026-08-02

This document records the target architecture for Harbor AI.

Harbor AI should not be treated as a local Markdown-only RAG demo. The target system is:

```text
Official web source based semantic RAG healthcare communication system
```

Official Ontario healthcare web pages should become the primary trusted source input. Curated Markdown should remain useful as seed knowledge, fallback knowledge, and a GitHub-readable source snapshot.

## 1. Core Decision

Harbor AI is not only a chatbot. It is an AI healthcare communication workflow.

The target system has two main pipelines:

```text
1. Indexing Pipeline
   Prepare trusted healthcare information as searchable knowledge.

2. User Query Pipeline
   Retrieve relevant knowledge based on user questions, transcripts, or Live Assist input, then generate safe communication support.
```

## 2. Six-Layer Architecture

The target architecture has six layers:

```text
1. Source Layer
2. Source Ingestion Layer
3. Document Processing Layer
4. Knowledge Index Layer
5. User Query Layer
6. Product Layer
```

## 3. Source Layer

The Source Layer contains trusted information sources.

Core source candidates:

```text
Ontario.ca
Health811
Health Care Connect
CPSO Doctor Search
College of Nurses of Ontario Registry
Ontario Health
Ontario Ministry of Health
```

The existing Markdown knowledge base should remain, but its role changes:

```text
curated seed knowledge
GitHub-readable source snapshot
fallback source for local development
```

In short:

```text
Official web pages = primary trusted source input
Markdown files = curated fallback and reviewable project source
```

## 4. Source Ingestion Layer

The Source Ingestion Layer loads source material into the system.

Target modules:

```text
source_registry.py
web_loader.py
markdown_loader.py
allowed_domains.py
```

Responsibilities:

```text
maintain official source URLs
restrict allowed domains
load official web page HTML
load local Markdown files
record source URL, retrieved_at, and source type
```

Important principles:

```text
Do not perform live open web search for every user query.
Do not use private clinic marketing pages as core factual sources.
Do not treat LLM-generated text as source material.
```

Recommended flow:

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

The Document Processing Layer converts raw source material into structured documents.

Target modules:

```text
text_extractor.py
structure_normalizer.py
toc_parser.py
semantic_chunker.py
metadata_augmenter.py
```

Responsibilities:

```text
extract main body text from web pages
remove navigation, footer, and repeated UI text
preserve headings, lists, and source references
normalize title, sections, and metadata
split content by semantic boundaries
add chunk metadata such as category, source, province, and use_case
```

TOC means Table of Contents. It is not image processing. It helps the system understand:

```text
H1
H2
H3
section order
```

If a separate TOC parser is too much at the beginning, this logic can live inside `structure_normalizer.py` or `semantic_chunker.py`.

## 6. Semantic Chunking

Harbor AI should not stay with simple paragraph chunking long term.

The target is semantic chunking:

```text
split by complete meaning units
preserve section headings
preserve source metadata
preserve safety context
make each chunk useful as an independent retrieval result
```

Examples:

```text
Chunk 1: What OHIP is
Chunk 2: What a health card is
Chunk 3: What to bring to a clinic
Chunk 4: How to describe symptoms
Chunk 5: When to seek emergency care
```

AI can help with:

```text
detecting chunk boundaries
generating chunk summaries
generating keywords
tagging use_case: prepare / live_assist
tagging safety relevance
```

## 7. Knowledge Index Layer

The Knowledge Index Layer turns processed chunks into searchable knowledge.

Target modules:

```text
embedding_service.py
vector_store_service.py
knowledge_index_service.py
indexing_harness.py
```

Responsibilities:

```text
call an AI embedding model
generate chunk embeddings
write vectors to Qdrant
update indexed versions of existing sources
provide a runnable entry point for the indexing pipeline
```

Qdrant is a vector database.

It stores:

```text
chunk text
chunk metadata
embedding vector
source information
```

Qdrant is not two separate databases. It is used in two phases:

```text
Indexing Pipeline: write to Qdrant
User Query Pipeline: retrieve from Qdrant
```

## 8. User Query Layer

The User Query Layer handles user input.

Target modules:

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

RAG belongs in the User Query Pipeline because it starts from the user query:

```text
user asks a question
↓
system retrieves relevant chunks
↓
LLM generates an answer using retrieved chunks
```

## 9. Product Layer

The Product Layer is the user-facing experience.

Harbor AI still has two core pages:

```text
Prepare
Live Assist
```

Prepare is responsible for:

```text
collecting visit reason
organizing symptom notes
generating checklists
generating questions to ask
generating Shared Context
```

Live Assist is responsible for:

```text
accepting transcript / speech-to-text input
using Shared Context
explaining clinician instructions
generating clear English phrases
providing multilingual communication support
summarizing follow-up notes
```

## 10. Out of Scope for Now

Harbor AI does not currently need:

```text
ACL resolver
Google OAuth
enterprise permission system
OCR PDF
image document processing
complex multi-agent workflows
```

Why:

```text
Harbor AI is a GitHub portfolio project, not a government enterprise document system.
The current focus is the AI healthcare communication workflow, not permissions or file integrations.
```

## 11. Recommended Development Order

Recommended order:

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

## 12. One-Sentence Architecture

Harbor AI's target architecture is:

```text
Trusted Ontario official web sources
→ AI-assisted semantic indexing
→ Qdrant vector retrieval
→ Shared Context
→ safety-aware LLM communication support
```

