# Harbor AI

Harbor AI is an AI-powered healthcare communication assistant for newcomers in Ontario.

It helps users prepare for non-emergency primary care visits and communicate more confidently during healthcare interactions by combining RAG, LLMs, speech-to-text, and shared visit context.

## Problem

Newcomers in Ontario often face more than a language barrier when using the healthcare system. They may not know where to seek care, what documents to bring, how to describe symptoms, or how to understand follow-up instructions.

Harbor AI focuses on healthcare communication support, not medical diagnosis.

## MVP Scope

The MVP focuses on non-emergency primary care communication in Ontario.

Core scenarios:

- Walk-in clinic visits
- Family doctor / nurse practitioner appointments

Out of scope for MVP:

- Medical diagnosis
- Emergency triage
- Insurance claims
- Appointment booking
- Long-term medical record management

## Core Features

### Prepare

The Prepare flow helps users get ready before a healthcare visit.

It can support:

- Visit type selection
- Symptom summary
- Pre-visit checklist
- Common questions from clinicians
- Questions users may want to ask
- Personalized visit notes

### Live Assist

The Live Assist flow helps users during healthcare conversations.

It can support:

- Text input
- Speech-to-text
- Translation
- Plain-language explanations
- Suggested phrases
- Visit summary

### Shared Context

Harbor AI connects preparation with live assistance through shared visit context.

The Prepare flow generates a visit context, and Live Assist reuses it to provide more relevant communication support.

## AI Architecture

Harbor AI is designed around four AI capabilities:

- LLM: generates visit briefs, explanations, suggested phrases, and summaries
- RAG: retrieves trusted Ontario healthcare navigation knowledge
- Speech AI: transcribes spoken input into text
- Shared Context: carries user-specific visit information across product flows

## Knowledge Base

The MVP knowledge base uses curated Markdown files based on public Ontario healthcare resources.

Initial scope:

```text
knowledge_base/
  ontario/
    primary_care/
    insurance/
    visit_preparation/
    safety/
```

The knowledge base is designed to support RAG retrieval for primary care communication scenarios.

## Tech Stack

Planned stack:

- Frontend: React + TypeScript
- Backend: FastAPI
- AI: OpenAI APIs
- Vector Database: Qdrant
- Knowledge Base: Markdown
- Deployment: Docker Compose

## Documentation

- [PRD](docs/PRD_EN.md)
- [SDD](docs/SDD_EN.md)

## Disclaimer

Harbor AI is not a medical diagnosis tool and does not replace doctors, nurses, pharmacists, emergency services, or licensed healthcare professionals.

For urgent or emergency situations, users should call 911 or seek immediate medical care.