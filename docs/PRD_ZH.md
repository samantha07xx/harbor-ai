# Harbor AI PRD

版本：v1.0  
日期：2026-07-09  
项目类型：GitHub Portfolio / AI Product Demo  
目标地区：Ontario, Canada  
MVP 范围：Non-emergency Primary Care Communication

## 1. 产品概述

Harbor AI 是一个面向 newcomers 的 AI 医疗沟通辅助产品，帮助用户在 Ontario 的非紧急 primary care 场景中提前准备就诊内容，并在看诊过程中更清楚地表达需求、理解医生或诊所工作人员的说明。

本项目不是诊断工具，也不替代医生、护士、药剂师或任何持牌医疗专业人员。它的核心定位是 healthcare communication support，而不是 medical decision-making。

一句话定位：

> Harbor AI helps newcomers prepare for primary care visits and communicate more confidently during healthcare interactions in Ontario.

## 2. 为什么做这个产品

Newcomers 在进入加拿大医疗系统时，经常遇到的困难不只是语言问题，还包括流程理解、信息准备和沟通焦虑。

典型问题包括：

- 不知道 walk-in clinic、family doctor、nurse practitioner、Health811 分别适合什么情况。
- 不知道看诊前需要带什么资料，例如 health card、身份文件、药物清单、症状记录。
- 不知道如何用英语描述症状、持续时间、严重程度、过敏史和既往病史。
- 担心听不懂医生的解释、检查建议、用药说明或 follow-up instructions。
- 临场紧张，忘记问重要问题。

Harbor AI 的价值在于把 “准备” 和 “现场沟通” 连接起来。用户在 Prepare 阶段生成的 visit context 会被 Live Assist 阶段复用，从而让 AI 不只是临时回答问题，而是理解用户当前这次看诊的背景。

## 3. 目标用户

### Primary Users

- 新移民
- 国际学生
- 临时工作签证持有人
- 英语能力有限、但需要独立处理基础医疗沟通的人

### Secondary Users

- 老年移民
- 陪同家人看诊的 family caregivers
- 帮助亲友准备就诊的人

## 4. MVP 范围

MVP 只聚焦 Ontario 的 non-emergency primary care 场景。

核心场景包括：

1. Walk-in clinic visit
2. Family doctor / nurse practitioner appointment

MVP 不覆盖急诊诊断、专科治疗、住院流程、保险理赔、牙科治疗、心理危机干预、长期病历管理或正式医疗建议。

范围定义：

> Harbor AI MVP focuses on helping newcomers prepare for and communicate during non-emergency primary care visits in Ontario, specifically walk-in clinic visits and family doctor / nurse practitioner appointments.

### 为什么只做 Primary Care

选择 primary care 是为了控制产品边界和医疗风险，同时让 GitHub 项目更清晰、可实现。

Primary care 适合 MVP 的原因：

- newcomer 高频使用
- 沟通准备需求明显
- 可以用公开官方资料构建知识库
- 风险低于 emergency 或 specialist care
- demo story 容易讲清楚
- 适合展示 RAG、LLM、Speech、Shared Context 的结合

## 5. 非目标

Harbor AI 在 MVP 阶段明确不做以下事情：

- 不提供诊断结论。
- 不判断用户是否患有某种疾病。
- 不决定用户是否需要药物、检查或治疗。
- 不替代医生、护士、药剂师或急救服务。
- 不处理真实保险理赔。
- 不做 appointment booking。
- 不长期保存完整个人病历。
- 不覆盖 emergency triage。

对于紧急情况，产品应提示用户拨打 911、前往 emergency department，或联系当地医疗服务。

## 6. 用户旅程

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

## 7. 核心页面

MVP 只做两个核心页面。

### 7.1 Prepare

目标：

帮助用户在看诊前完成信息准备，减少临场焦虑和遗漏。

核心功能：

- 选择看诊类型：walk-in clinic 或 family doctor / nurse practitioner
- 输入症状、持续时间、严重程度、相关背景
- 生成就诊前 checklist
- 解释常见 healthcare terminology
- 提供可能会被问到的问题
- 提供用户可以主动问医生的问题
- 生成 personalized visit notes
- 生成 Shared Context，供 Live Assist 使用

Prepare 的 AI 能力主要依赖：

- RAG：检索 Ontario primary care 相关知识
- LLM：整理用户输入，生成清晰的 visit brief

### 7.2 Live Assist

目标：

在看诊或沟通过程中帮助用户理解对话内容，并生成表达建议。

核心功能：

- 用户输入或语音转文字
- 根据 Shared Context 理解当前看诊背景
- 将用户想说的话转成更清楚的英文表达
- 解释医生或诊所工作人员的说明
- 生成 follow-up questions
- 提供简短翻译
- 总结 visit takeaways

Live Assist 的 AI 能力主要依赖：

- Speech AI：将语音转成文本
- LLM：生成沟通建议、解释和翻译
- Shared Context：提供用户这次看诊的背景
- RAG：在需要时检索 healthcare navigation 知识

Vision AI 可以作为 optional demo，例如识别诊所表格、药瓶标签或现场标识，但不属于 MVP 必须完成的核心功能。

## 8. Shared Context 设计

Shared Context 是 Harbor AI 的核心创新点。

Prepare 阶段生成的上下文会被保存，并在 Live Assist 阶段复用。这样用户不需要重复解释自己为什么来看病、有哪些症状、已经准备了哪些问题。

流程：

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

Shared Context 内容示例：

- Visit type
- Symptoms summary
- Duration and severity
- User concerns
- Documents to bring
- Questions to ask
- Relevant Ontario healthcare guidance
- Preferred language
- Communication goal

产品说明：

> Harbor AI uses a shared context layer that combines RAG-based healthcare knowledge with user-specific visit context. This makes the Live Assist experience more personalized, continuous, and situation-aware.

这里的重点不是单纯做 RAG，而是展示 Context Engineering：AI 不只检索知识，还能在用户旅程的不同阶段持续使用上下文。

## 9. Source / Knowledge Base 形式

MVP 的 source 使用 curated Markdown documents。

也就是说，Harbor AI 不在运行时实时抓取网页，而是先从官方或可信来源整理内容，写成结构化 Markdown 文件，再进行 chunking、embedding 和 vector retrieval。

推荐目录：

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

每个 Markdown 文件建议使用统一格式：

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

RAG 流程：

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

## 10. 官方 Source 网站

MVP 的知识库建议只使用 Ontario 相关的官方或高度可信来源。

核心来源：

- Ontario.ca - Health care in Ontario: https://www.ontario.ca/page/health-care-ontario
- Ontario.ca - Apply for OHIP and get a health card: https://www.ontario.ca/page/apply-ohip-and-get-health-card
- Ontario.ca - What OHIP covers: https://www.ontario.ca/page/what-ohip-covers
- Ontario.ca - Find a doctor or nurse practitioner: https://www.ontario.ca/page/find-family-doctor-or-nurse-practitioner
- Health811 Ontario: https://health811.ontario.ca/
- Health Care Connect: https://hcc3.hcc.moh.gov.on.ca/
- College of Physicians and Surgeons of Ontario - Find a Doctor: https://doctors.cpso.on.ca/
- College of Nurses of Ontario - Nurse Registry: https://registry.cno.org/
- Ontario Ministry of Health: https://www.ontario.ca/page/ministry-health

辅助来源：

- 211 Ontario: https://211ontario.ca/
- Ontario Health: https://www.ontariohealth.ca/

使用原则：

- 优先使用 Ontario government 和 official healthcare organization 的页面。
- 每个 Markdown source 文件必须保留来源 URL。
- 不把 AI 输出当作知识库 source。
- 不抓取私人诊所营销页作为核心事实来源。
- 如果官方信息变化，应重新整理 Markdown 并重新生成 embeddings。

## 11. AI 架构

Harbor AI 的 AI 系统分为四个模块。

### 11.1 LLM

负责：

- 生成 visit brief
- 改写用户表达
- 生成 follow-up questions
- 总结医生说明
- 翻译和解释 healthcare terminology

### 11.2 RAG

负责：

- 检索 Ontario primary care 知识
- 支持 Prepare 页面生成 checklist 和说明
- 支持 Live Assist 回答 healthcare navigation 问题

### 11.3 Speech AI

负责：

- 将用户语音或现场对话片段转成文字
- 为 Live Assist 提供输入

### 11.4 Vision AI

MVP optional。

可能负责：

- 识别诊所表格中的字段
- 识别药瓶标签或说明
- 识别现场标识

Vision AI 不作为 MVP 核心成功标准。

## 12. 技术架构

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

主要组件：

- Frontend：React + TypeScript
- Backend：FastAPI
- AI APIs：OpenAI GPT, Speech-to-text, Embeddings
- Vector Database：Qdrant
- Knowledge Base：Markdown files
- Deployment：Docker Compose

## 13. 数据和隐私原则

Harbor AI 涉及健康相关沟通，因此必须采用保守的数据设计。

原则：

- 最小化收集用户信息。
- 默认不要求真实姓名、health card number 或完整出生日期。
- Visit Context 只保存完成 demo 所需的信息。
- 明确告诉用户产品不是医疗诊断工具。
- 不把用户输入直接加入公共知识库。
- 不输出诊断、处方或治疗决定。
- 对 emergency 相关输入触发安全提示。

## 14. 成功指标

产品指标：

- 用户是否能完成 Prepare flow
- 用户生成 visit brief 所需时间
- 用户是否能在 Live Assist 中复用 Prepare context
- 用户满意度
- 用户是否觉得就诊前更有准备

AI 指标：

- RAG retrieval relevance
- LLM response helpfulness
- Hallucination rate
- Speech transcription quality
- Context reuse accuracy
- Live Assist response latency

工程指标：

- API response time
- Embedding pipeline success rate
- Vector database retrieval latency
- Error rate

## 15. Demo Scenario

用户：刚到 Ontario 的国际学生。  
问题：胃痛三天，想去 walk-in clinic，但不知道怎么描述症状，也不知道要带什么。  

Prepare：

- 用户选择 walk-in clinic。
- 输入症状、持续时间、严重程度、是否发烧、是否吃过药。
- Harbor AI 基于 Ontario primary care knowledge base 生成 checklist、常见问题、可用表达和 visit brief。

Live Assist：

- 用户在诊所听到工作人员或医生的说明。
- Harbor AI 根据之前生成的 Shared Context 帮助用户理解说明。
- 用户可以输入 “I want to ask if I need a test”，系统生成更自然、清楚的英文表达。
- 看诊结束后，系统总结 follow-up instructions。

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

Harbor AI MVP 是一个面向 Ontario newcomers 的 AI healthcare communication assistant。它使用 curated Markdown knowledge base、RAG、LLM、Speech AI 和 Shared Context，帮助用户准备并完成 non-emergency primary care 沟通。

MVP 只聚焦两个场景：

- Walk-in clinic
- Family doctor / nurse practitioner appointment

核心产品亮点：

> Prepare generates the context. Live Assist reuses the context. RAG provides trusted healthcare navigation knowledge. LLM turns that knowledge into communication support.

