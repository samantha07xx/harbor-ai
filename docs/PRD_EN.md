# Harbor AI PRD

Version: v1.0  
Date: 2026-07-09  
Project Type: GitHub Portfolio / AI Product Demo  
Target Region: Ontario, Canada  
MVP Scope: Non-emergency Primary Care Communication

## 1. Product Overview

Harbor AI is an AI-powered healthcare communication assistant for newcomers in Ontario. It helps users prepare for non-emergency primary care visits and communicate more clearly during healthcare interactions.

The product is not a diagnostic tool and does not replace doctors, nurses, pharmacists, emergency services, or licensed healthcare professionals. Its core role is healthcare communication support, not medical decision-making.

One-sentence positioning:

> Harbor AI helps newcomers prepare for primary care visits and communicate more confidently during healthcare interactions in Ontario.

## 2. Why This Product

Newcomers often face more than a language barrier when using the Canadian healthcare system. They also need to understand care pathways, prepare the right information, and communicate under stress.

Common problems include:

- Not knowing when to use a walk-in clinic, family doctor, nurse practitioner, or Health811.
- Not knowing what to bring to a visit, such as a health card, identity document, medication list, or symptom notes.
- Not knowing how to describe symptoms, duration, severity, allergies, and medical history in English.
- Worrying about misunderstanding instructions, tests, medication guidance, or follow-up steps.
- Forgetting important questions during the visit.

Harbor AI creates value by connecting preparation with real-time support. The visit context created during the Prepare flow is reused during Live Assist, allowing the AI to understand the user’s current healthcare interaction instead of responding as a generic chatbot.

## 3. Target Users

### Primary Users

- New immigrants
- International students
- Temporary workers
- People with limited English proficiency who need to handle basic healthcare communication independently

### Secondary Users

- Elderly immigrants
- Family caregivers
- People helping relatives prepare for healthcare visits

## 4. MVP Scope

The MVP focuses only on non-emergency primary care scenarios in Ontario.

Core scenarios:

1. Walk-in clinic visit
2. Family doctor / nurse practitioner appointment

The MVP does not cover emergency diagnosis, specialist treatment, hospital admission, insurance claims, dental treatment, mental health crisis support, long-term medical record management, or formal medical advice.

Scope statement:

> Harbor AI MVP focuses on helping newcomers prepare for and communicate during non-emergency primary care visits in Ontario, specifically walk-in clinic visits and family doctor / nurse practitioner appointments.

### Why Primary Care Only

Primary care keeps the product focused, realistic, and safer for a GitHub MVP.

Primary care is suitable for the MVP because:

- It is a high-frequency use case for newcomers.
- Communication preparation is a clear user need.
- Public official sources can support the knowledge base.
- It has lower risk than emergency or specialist care.
- The demo story is easy to understand.
- It allows the project to show RAG, LLM, Speech AI, and Shared Context in one coherent product flow.

## 5. Non-Goals

Harbor AI does not do the following in the MVP:

- It does not provide diagnoses.
- It does not determine whether a user has a specific disease.
- It does not decide whether a user needs medication, tests, or treatment.
- It does not replace doctors, nurses, pharmacists, or emergency services.
- It does not process real insurance claims.
- It does not book appointments.
- It does not store a complete personal medical record.
- It does not perform emergency triage.

For urgent or emergency situations, the product should direct users to call 911, go to an emergency department, or contact local healthcare services.

## 6. User Journey

```text
Need Medical Help
        ↓
Choose Care Type
        ↓
Prepare for Visit
        ↓
Generate Visit Context
        ↓
Go to Clinic / Appointment
        ↓
Use Live Assist
        ↓
Understand Instructions
        ↓
Leave with Confidence
```

## 7. Core Pages

The MVP has two core pages.

### 7.1 Prepare

Goal:

Help users prepare before a healthcare visit and reduce anxiety or missing information.

Core features:

- Select visit type: walk-in clinic or family doctor / nurse practitioner
- Enter symptoms, duration, severity, and relevant background
- Generate a pre-visit checklist
- Explain common healthcare terminology
- Provide likely questions from the clinician or clinic staff
- Suggest questions the user may want to ask
- Generate personalized visit notes
- Generate Shared Context for Live Assist

Primary AI capabilities:

- RAG: retrieves Ontario primary care knowledge
- LLM: organizes user input into a clear visit brief

### 7.2 Live Assist

Goal:

Help users understand conversation content and produce clearer responses during the visit.

Core features:

- Text input or speech-to-text input
- Use Shared Context to understand the current visit
- Rewrite what the user wants to say into clear English
- Explain instructions from clinicians or clinic staff
- Generate follow-up questions
- Provide short translations
- Summarize visit takeaways

Primary AI capabilities:

- Speech AI: transcribes voice into text
- LLM: generates communication suggestions, explanations, and translations
- Shared Context: provides the user’s visit background
- RAG: retrieves healthcare navigation knowledge when needed

Vision AI can be included as an optional demo, such as recognizing clinic forms, medication labels, or signs. It is not required for MVP success.

## 8. Shared Context Design

Shared Context is the core product innovation in Harbor AI.

The context created during Prepare is saved and reused during Live Assist. This prevents users from repeatedly explaining why they are visiting, what symptoms they have, and what they already prepared.

Flow:

```text
Prepare Page
    ↓
User Input + RAG Knowledge
    ↓
Generate Visit Context
    ↓
Store Context
    ↓
Live Assist Retrieves Context
    ↓
LLM Generates Context-Aware Support
```

Shared Context may include:

- Visit type
- Symptom summary
- Duration and severity
- User concerns
- Documents to bring
- Questions to ask
- Relevant Ontario healthcare guidance
- Preferred language
- Communication goal

Product statement:

> Harbor AI uses a shared context layer that combines RAG-based healthcare knowledge with user-specific visit context. This makes the Live Assist experience more personalized, continuous, and situation-aware.

The key idea is not simply RAG. The project demonstrates Context Engineering: AI retrieves trusted knowledge and also carries user-specific context across stages of the healthcare communication journey.

## 9. Source / Knowledge Base Format

The MVP uses curated Markdown documents as the knowledge source.

Harbor AI does not scrape websites at runtime. Instead, official or trusted healthcare information is manually curated into structured Markdown files. These files are then chunked, embedded, and stored for vector retrieval.

Recommended structure:

```text
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
```

Each Markdown file should use a consistent structure:

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

RAG pipeline:

```text
Official Websites
    ↓
Curated Markdown
    ↓
Chunking
    ↓
Embedding
    ↓
Qdrant Vector Database
    ↓
Retrieval
    ↓
LLM Response
```

## 10. Official Source Websites

The MVP knowledge base should use Ontario-specific official or highly trusted sources.

Core sources:

- Ontario.ca - Health care in Ontario: https://www.ontario.ca/page/health-care-ontario
- Ontario.ca - Apply for OHIP and get a health card: https://www.ontario.ca/page/apply-ohip-and-get-health-card
- Ontario.ca - What OHIP covers: https://www.ontario.ca/page/what-ohip-covers
- Ontario.ca - Find a doctor or nurse practitioner: https://www.ontario.ca/page/find-family-doctor-or-nurse-practitioner
- Health811 Ontario: https://health811.ontario.ca/
- Health Care Connect: https://hcc3.hcc.moh.gov.on.ca/
- College of Physicians and Surgeons of Ontario - Find a Doctor: https://doctors.cpso.on.ca/
- College of Nurses of Ontario - Nurse Registry: https://registry.cno.org/
- Ontario Ministry of Health: https://www.ontario.ca/page/ministry-health

Supporting sources:

- 211 Ontario: https://211ontario.ca/
- Ontario Health: https://www.ontariohealth.ca/

Source principles:

- Prioritize Ontario government and official healthcare organization pages.
- Keep source URLs inside each Markdown source file.
- Do not treat AI-generated text as knowledge base source material.
- Do not use private clinic marketing pages as core factual sources.
- If official information changes, update the Markdown files and regenerate embeddings.

## 11. AI Architecture

Harbor AI contains four AI modules.

### 11.1 LLM

Responsibilities:

- Generate visit briefs
- Rewrite user expressions
- Generate follow-up questions
- Summarize clinician instructions
- Translate and explain healthcare terminology

### 11.2 RAG

Responsibilities:

- Retrieve Ontario primary care knowledge
- Support Prepare checklists and explanations
- Support Live Assist healthcare navigation answers

### 11.3 Speech AI

Responsibilities:

- Transcribe user speech or short conversation segments
- Provide input for Live Assist

### 11.4 Vision AI

Optional for MVP.

Possible responsibilities:

- Recognize fields on clinic forms
- Recognize medication labels or instructions
- Recognize signs in the clinic environment

Vision AI is not a core success requirement for the MVP.

## 12. Technical Architecture

```text
React + TypeScript Frontend
        ↓
FastAPI Backend
        ↓
Context Service
        ↓
AI Orchestration Layer
        ↓
OpenAI APIs
        ↓
Qdrant Vector Database
        ↓
Markdown Knowledge Base
        ↓
Docker Compose
```

Main components:

- Frontend: React + TypeScript
- Backend: FastAPI
- AI APIs: OpenAI GPT, speech-to-text, embeddings
- Vector Database: Qdrant
- Knowledge Base: Markdown files
- Deployment: Docker Compose

## 13. Data and Privacy Principles

Harbor AI handles health-related communication, so the product should use conservative data design.

Principles:

- Collect the minimum amount of user information.
- Do not require real names, health card numbers, or full birth dates by default.
- Store only the visit context needed for the demo.
- Clearly state that the product is not a diagnostic tool.
- Do not add user input directly into the public knowledge base.
- Do not generate diagnoses, prescriptions, or treatment decisions.
- Trigger safety guidance for emergency-related inputs.

## 14. Success Metrics

Product metrics:

- Whether users can complete the Prepare flow
- Time needed to generate a visit brief
- Whether Live Assist successfully reuses Prepare context
- User satisfaction
- Whether users feel more prepared before the visit

AI metrics:

- RAG retrieval relevance
- LLM response helpfulness
- Hallucination rate
- Speech transcription quality
- Context reuse accuracy
- Live Assist response latency

Engineering metrics:

- API response time
- Embedding pipeline success rate
- Vector database retrieval latency
- Error rate

## 15. Demo Scenario

User: An international student who recently arrived in Ontario.  
Problem: The user has had stomach pain for three days and wants to visit a walk-in clinic, but does not know how to describe the symptoms or what to bring.  

Prepare:

- The user selects walk-in clinic.
- The user enters symptoms, duration, severity, fever status, and medications taken.
- Harbor AI uses the Ontario primary care knowledge base to generate a checklist, likely questions, useful phrases, and a visit brief.

Live Assist:

- The user hears instructions from clinic staff or the clinician.
- Harbor AI uses the previously generated Shared Context to help the user understand the instructions.
- The user types “I want to ask if I need a test,” and the system rewrites it into clearer English.
- After the visit, the system summarizes follow-up instructions.

## 16. Roadmap

### Version 1 - MVP

- Prepare page
- Live Assist page
- Markdown knowledge base
- RAG pipeline
- Shared Context
- Text input
- Basic speech-to-text
- Docker Compose setup

### Version 2

- OCR for clinic forms
- TTS response
- Medication label explanation
- Multilingual UI
- Better visit summary export
- Appointment preparation templates

### Version 3

- Personal healthcare timeline
- Calendar integration
- AI agent workflows
- MCP integration
- Secure account system
- Family caregiver mode

## 17. Design Principles

1. AI serves the user journey, not the other way around.
2. Preparation is as important as real-time assistance.
3. Context should persist across interactions.
4. Every AI module should have a clear responsibility.
5. The system should reduce anxiety, not increase cognitive load.
6. Medical safety matters more than feature breadth.
7. The product should help users communicate, not make medical decisions for them.

## 18. Final MVP Definition

Harbor AI MVP is an AI healthcare communication assistant for newcomers in Ontario. It uses a curated Markdown knowledge base, RAG, LLM, Speech AI, and Shared Context to help users prepare for and complete non-emergency primary care communication.

The MVP focuses on two scenarios:

- Walk-in clinic
- Family doctor / nurse practitioner appointment

Core product insight:

> Prepare generates the context. Live Assist reuses the context. RAG provides trusted healthcare navigation knowledge. LLM turns that knowledge into communication support.

