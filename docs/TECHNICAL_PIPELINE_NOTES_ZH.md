# Harbor AI Technical Pipeline Notes

Date: 2026-07-13

This document records the technical architecture direction discussed for Harbor AI. The goal is to align the project with a more complete AI RAG architecture, organized around two major pipelines:

- Indexing Pipeline
- User Query Pipeline

Harbor AI should not be treated as a simple demo with only basic chunking. The target architecture should directly reflect the intended final direction: semantic indexing, AI embeddings, vector retrieval, shared context, and safety-aware LLM responses.

## 1. Core Architecture Decision

Harbor AI should follow a two-pipeline architecture:

```text
A. Indexing Pipeline
Prepare trusted healthcare knowledge so it can be searched later.

B. User Query Pipeline
Use a user question or live transcript to retrieve relevant knowledge and generate a helpful response.
```

This structure is similar to mature RAG systems:

```text
Source documents / web pages
↓
extraction and normalization
↓
semantic chunking
↓
embeddings
↓
vector database
↓
retrieval
↓
LLM response
```

## 2. Indexing Pipeline

The Indexing Pipeline processes information before the user asks a question.

Target flow:

```text
Ontario trusted sources
↓
source loader
↓
text extractor / parser
↓
structure normalizer
↓
semantic chunker
↓
AI embedding service
↓
Qdrant vector database
```

Its purpose is to turn Ontario healthcare source material into searchable knowledge.

## 3. Source Layer

Harbor AI should use two source formats:

```text
Official Ontario web pages
Curated Markdown files
```

Official Ontario web pages should be the primary trusted source input.

Markdown remains useful as seed knowledge, fallback content, local development material, and a GitHub-readable source snapshot.

Harbor AI should not fetch websites every time a user asks a question. Instead, official web content should be pulled into an indexing workflow:

```text
official website
↓
load / extract text
↓
normalize structure
↓
chunk
↓
embed
↓
store in Qdrant
```

This keeps user responses faster and more stable.

## 4. Parser and Extractor

Parser and extractor logic is needed because raw web pages contain extra material such as navigation, footers, buttons, repeated links, and layout text.

The extractor should focus on useful healthcare content:

```text
page title
main body text
headings
lists
source URL
retrieval date
```

For Harbor AI, this should support official web pages and Markdown seed files through the same normalized document format.

## 5. Structure Normalizer

The structure normalizer converts different source formats into a common internal shape.

Example normalized structure:

```json
{
  "title": "OHIP Basics",
  "source_type": "official_web",
  "source_url": "https://www.ontario.ca/page/apply-ohip-and-get-health-card",
  "source_path": null,
  "province": "ontario",
  "category": "insurance",
  "sections": []
}
```

This helps the rest of the pipeline work consistently, whether the original source was an official web page or a Markdown seed file.

## 6. TOC Parser

TOC means Table of Contents.

It is not for images. It is for understanding document structure:

```text
H1 title
H2 section
H3 subsection
section order
```

For Harbor AI, a separate TOC parser is not necessary at the beginning. The useful part can be included in the structure normalizer and semantic chunker.

## 7. Semantic Chunking and Augmentation

Chunking means splitting a long document into smaller units that can be retrieved later.

Harbor AI should move toward semantic chunking, not only paragraph splitting.

Semantic chunking should try to keep one complete idea together:

```text
What OHIP is
What a health card is
What to bring to a clinic
When to seek emergency care
How to describe symptoms
```

Augmentation means adding helpful metadata to each chunk.

Possible chunk metadata:

```json
{
  "chunk_id": "ontario-insurance-ohip-basics-001",
  "title": "OHIP Basics",
  "section": "What OHIP Is",
  "category": "insurance",
  "province": "ontario",
  "use_case": ["prepare", "live_assist"],
  "source_path": "knowledge_base/ontario/insurance/ohip_basics.md",
  "source_url": "https://www.ontario.ca/page/apply-ohip-and-get-health-card"
}
```

Semantic chunking can later use AI to help identify boundaries, generate summaries, or add keywords.

## 8. Embedding Service

Embedding turns text into vectors so the system can compare meaning.

Example:

```text
"I do not have OHIP yet."
↓
[0.12, -0.03, 0.88, ...]
```

In the final architecture, embeddings should use an AI embedding model, such as OpenAI embeddings.

The current mock embedding service is only a temporary local scaffold. It defines the interface and lets the pipeline be developed without API cost or API keys. The intended direction is real AI embeddings.

## 9. Qdrant Vector Database

Qdrant is the local vector database.

It stores:

```text
chunk text
chunk metadata
chunk embedding vector
```

It is used by both pipelines, but not as two separate databases.

In the Indexing Pipeline:

```text
write chunks and embeddings into Qdrant
```

In the User Query Pipeline:

```text
search Qdrant for chunks similar to the user query
```

So Qdrant has two roles:

```text
index-time storage
query-time retrieval
```

## 10. User Query Pipeline

The User Query Pipeline starts when a user asks a question or uses Live Assist.

Target flow:

```text
user question / transcript
↓
shared context
↓
query rewriting
↓
query embedding
↓
Qdrant retrieval
↓
safety layer
↓
LLM response
```

This is where RAG happens.

## 11. Why RAG Belongs in the User Query Pipeline

Chunking processes the knowledge that will be searched later.

RAG starts from the user query:

```text
user asks a question
↓
system embeds the question
↓
system retrieves relevant chunks
↓
LLM answers using retrieved chunks
```

So the Indexing Pipeline prepares searchable knowledge, while the User Query Pipeline uses that knowledge to answer a specific user question.

## 12. LLM Role

The LLM does not replace the vector database.

The LLM is responsible for:

```text
understanding intent
rewriting queries
generating explanations
translating or simplifying language
creating suggested phrases
using shared context
following safety boundaries
```

In Prepare, the LLM can generate:

```text
visit brief
questions to ask
document checklist
symptom summary
shared context
```

In Live Assist, the LLM can generate:

```text
clear English phrases
plain-language explanations
translation support
follow-up questions
visit takeaways
```

## 13. Modules Not Needed for MVP

Some parts from the reference architecture are not needed for Harbor AI right now.

ACL Resolver:

```text
Not needed for MVP.
Harbor AI does not currently manage private government files, enterprise permissions, or user access control.
```

OCR PDF:

```text
Not needed for MVP.
Harbor AI will focus on website text and Markdown knowledge sources, not scanned PDFs or image-based documents.
```

Google OAuth:

```text
Not needed for MVP.
Harbor AI does not require user login at the current stage.
```

## 14. Current Implementation Status

Already implemented:

```text
knowledge_base/ontario/**/*.md
backend/app/utils/markdown_loader.py
backend/app/utils/text_chunker.py
backend/app/services/embedding_service.py
```

The current code has:

```text
Official web-source loading
Markdown seed/fallback loading
paragraph-based chunking
mock deterministic embedding service
```

The desired direction is:

```text
Official web-source loading
Markdown seed/fallback loading
structure normalization
semantic chunking
AI embeddings
Qdrant vector storage
semantic RAG retrieval
safety-aware LLM response
```

## 15. Proposed Target Backend Structure

Possible future structure:

```text
backend/app/
  api/
    health.py
    prepare.py
    knowledge_base.py

  loaders/
    markdown_loader.py
    web_loader.py

  processors/
    text_extractor.py
    structure_normalizer.py
    semantic_chunker.py

  services/
    embedding_service.py
    knowledge_index_service.py
    vector_store_service.py
    rag_service.py
    query_rewriter_service.py
    llm_service.py
    safety_service.py
    context_service.py

  models/
    knowledge.py
    requests.py
    responses.py
```

This structure should be introduced gradually, but the architecture direction should be treated as the target design.
