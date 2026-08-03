# Harbor AI Project Workflow Notes

Date: 2026-07-13

This document records the product and workflow decisions discussed today. It focuses on how Harbor AI should be built from this point forward.

## 1. Product Direction

Harbor AI is an AI-powered healthcare communication assistant for newcomers in Ontario.

The product should remain focused on:

```text
non-emergency primary care communication
```

Core user journey:

```text
Prepare before a visit
↓
generate shared context
↓
use Live Assist during the interaction
↓
receive context-aware communication support
```

Harbor AI should not be positioned as a diagnosis product or emergency triage product.

## 2. Architecture Direction

The project should follow the more mature two-pipeline architecture discussed today:

```text
Indexing Pipeline
User Query Pipeline
```

This direction fits Harbor AI because the project needs both:

```text
trusted healthcare knowledge processing
```

and:

```text
context-aware user support
```

## 3. No Separate "Basic Version" Framing

The project should not be described as having a separate basic version.

Instead, the intended architecture should be the target architecture from now on:

```text
semantic chunking
AI embeddings
Qdrant vector retrieval
RAG
LLM response generation
shared context
safety layer
```

Implementation can still happen step by step, but the design direction should be the final intended architecture.

In other words:

```text
Architecture target: final AI RAG system
Implementation method: small safe steps
```

## 4. What We Borrow From the Reference Architecture

Useful ideas to borrow:

```text
Indexing Pipeline
User Query Pipeline
source loading
text extraction
structure normalization
semantic chunking
augmentation
local vector database
semantic RAG
LLM response
safe fallback
```

Ideas not needed right now:

```text
ACL resolver
Google OAuth
enterprise access control
OCR PDF
image document processing
```

The reference project appears more enterprise/government-oriented. Harbor AI is a GitHub portfolio project, so it should borrow the architecture pattern without inheriting unnecessary complexity.

## 5. Source Strategy

Harbor AI should use trusted Ontario healthcare sources.

Primary source form:

```text
official Ontario web pages
```

Supporting source form:

```text
curated Markdown seed/fallback files
```

Important decision:

```text
Do not retrieve websites live for every user question.
```

Instead:

```text
official source URLs
↓
indexing pipeline
↓
Qdrant
↓
query-time retrieval
```

This makes the product more stable and easier to explain. Markdown stays useful as a GitHub-readable source snapshot, but it should not be the only long-term source type.

## 6. Chunking Direction

The current paragraph-based chunking should be treated as a scaffold, not the desired final method.

The desired method is:

```text
semantic chunking
```

Semantic chunking should preserve meaningful units, such as:

```text
OHIP basics
what to bring
symptom description
emergency safety limits
questions to ask
after-visit instructions
```

The future chunking system should understand headings, sections, source metadata, and the user journey.

## 7. Embedding Direction

The current mock embedding service is useful for scaffolding, but the intended direction is AI embeddings.

Final target:

```text
OpenAI embedding model
```

Purpose:

```text
turn healthcare text into vectors
compare semantic similarity
retrieve relevant knowledge chunks
```

This supports RAG and makes the Prepare / Live Assist responses source-grounded.

## 8. Qdrant Direction

Qdrant should be the local vector database.

It is not two different databases for two sides of the system.

It is one vector database used in two ways:

```text
Indexing Pipeline writes to Qdrant.
User Query Pipeline reads from Qdrant.
```

This should be explained clearly in project documentation because it is an important RAG concept.

## 9. LLM Direction

The LLM should not be described as the whole RAG system.

The LLM is one component in the query pipeline.

It should help with:

```text
query rewriting
answer generation
translation
plain-language explanation
suggested phrases
shared context reasoning
safety-aware wording
```

The LLM should answer using retrieved knowledge and should respect Harbor AI's safety boundaries.

## 10. Safety Direction

Safety remains essential because Harbor AI is in a healthcare communication domain.

The system should continue to state:

```text
Harbor AI does not diagnose.
Harbor AI does not replace clinicians.
Harbor AI does not perform emergency triage.
Urgent symptoms should lead users to 911 or emergency care.
```

The future query pipeline should include a safety layer before or during LLM response generation.

## 11. Current Project State

The project currently has:

```text
README.md
docs/PRD_EN.md
docs/SDD_EN.md
knowledge_base/ontario/**/*.md
FastAPI backend
health API
prepare API skeleton
knowledge base API
Official web source registry
web_loader
Markdown seed loader
text chunker scaffold
mock embedding service
```

Current uncommitted work:

```text
backend/app/services/
```

This contains the embedding service skeleton and mock embedding implementation.

## 12. Recommended Next Steps

The next technical steps should align with the final architecture:

```text
1. Commit current embedding service after review.
2. Add knowledge_index_service.py as the indexing orchestrator.
3. Start moving toward semantic chunking.
4. Add metadata augmentation for chunks.
5. Add OpenAI embedding support.
6. Add Qdrant vector store integration.
7. Add semantic RAG retrieval.
8. Add LLM response generation.
9. Add shared context.
10. Add Live Assist query flow.
```

The order can change slightly, but the target architecture should stay consistent.

## 13. Collaboration Rules Going Forward

The working style should remain beginner-friendly and controlled.

Rules:

```text
1. Before starting, explain the plan.
2. Before editing, say which files will change.
3. Before testing, say what will be tested and why.
4. Before commit, stop and show git status.
5. Before push, ask for confirmation.
```

Additional preferences:

```text
explain steps in Chinese
avoid doing too much at once
test after meaningful changes
keep technical learning notes
keep project build/process notes
```

## 14. Today's Main Decision

Today's main decision:

```text
Harbor AI should adopt the mature RAG pipeline structure directly.
```

The project should be built toward:

```text
AI semantic indexing
AI embeddings
Qdrant retrieval
shared context
safety-aware LLM communication support
```

This makes Harbor AI stronger as a GitHub portfolio project because it shows not only feature implementation, but also AI product architecture thinking.
