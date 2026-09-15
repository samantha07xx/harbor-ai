import { ArrowUp, Database, ExternalLink, LoaderCircle, RotateCcw, ShieldCheck } from "lucide-react";
import { FormEvent, useMemo, useRef, useState } from "react";

import { sendChatMessage } from "./api";
import type { ChatMessage } from "./types";

const starterPrompts = [
  "How do I apply for OHIP?",
  "What documents do I need for a health card?",
  "Can I get care before OHIP?",
];

const initialMessages: ChatMessage[] = [
  {
    id: "welcome",
    role: "assistant",
    content: "Welcome to Harbor. Ask an Ontario healthcare navigation question to search trusted sources.",
    citations: [],
  },
];

function metadataLabel(value: unknown): string | null {
  if (typeof value !== "string" || value.length === 0) {
    return null;
  }

  return value
    .split("_")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function statusBadges(metadata?: Record<string, unknown>): string[] {
  if (!metadata) {
    return [];
  }

  const badges: string[] = [];
  const status = metadata.implementation_status;
  const agentMode = metadata.agent_mode;
  const plannerRoute = metadata.planner_route;
  const safetyRoute = metadata.safety_route;
  const intent = metadata.detected_intent;
  const toolName = metadata.tool_name;
  const corpusMode = metadata.retrieval_corpus_mode;
  const answerMode = metadata.answer_mode;

  if (status === "deterministic_agent_safety") {
    badges.push("Safety");
  } else if (status === "deterministic_agent_local_rag") {
    badges.push("Local RAG");
  } else if (status === "openai_agent_tool_rag") {
    badges.push("Agent RAG");
  } else if (status === "openai_rate_limited") {
    badges.push("OpenAI rate limit");
  }

  const agentLabel = metadataLabel(agentMode);
  if (agentLabel === "Openai React Planner") {
    badges.push("ReAct Planner");
  }

  const plannerLabel = metadataLabel(plannerRoute);
  if (plannerLabel) {
    badges.push(plannerLabel);
  }

  const routeLabel = metadataLabel(safetyRoute);
  if (routeLabel && routeLabel !== "Proceed") {
    badges.push(routeLabel);
  }

  const intentLabel = metadataLabel(intent);
  if (intentLabel) {
    badges.push(intentLabel);
  }

  const toolLabel = metadataLabel(toolName);
  if (toolLabel) {
    badges.push(toolLabel);
  }

  const corpusLabel = metadataLabel(corpusMode);
  if (corpusLabel) {
    badges.push(corpusLabel);
  }

  const answerLabel = metadataLabel(answerMode);
  if (answerLabel) {
    badges.push(answerLabel);
  }

  return badges;
}

function MetadataBadges({ metadata }: { metadata?: Record<string, unknown> }) {
  const badges = statusBadges(metadata);

  if (badges.length === 0) {
    return null;
  }

  return (
    <div className="metadata-badges" aria-label="Response metadata">
      {badges.map((badge) => (
        <span key={badge}>{badge}</span>
      ))}
    </div>
  );
}

export function App() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionId = useMemo(() => crypto.randomUUID(), []);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedInput = input.trim();

    if (!trimmedInput || isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedInput,
      citations: [],
    };

    setMessages((currentMessages) => [...currentMessages, userMessage]);
    setInput("");
    setError(null);
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        session_id: sessionId,
        message: trimmedInput,
        user_context: { province: "Ontario" },
      });

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.answer,
          citations: response.citations,
          metadata: response.metadata,
          suggestedFollowups: response.suggested_followups,
        },
      ]);
    } catch {
      setError("Harbor could not reach the backend. Make sure the API is running.");
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }

  function resetChat() {
    setMessages(initialMessages);
    setInput("");
    setError(null);
    inputRef.current?.focus();
  }

  function usePrompt(prompt: string) {
    setInput(prompt);
    inputRef.current?.focus();
  }

  return (
    <main className="app-shell">
      <section className="chat-workspace" aria-label="Harbor chat">
        <header className="top-bar">
          <div>
            <p className="eyebrow">Ontario healthcare navigation</p>
            <h1>Harbor</h1>
            <div className="runtime-strip" aria-label="Runtime status">
              <span>
                <ShieldCheck size={14} aria-hidden="true" />
                Agentic RAG
              </span>
              <span>
                <Database size={14} aria-hidden="true" />
                Trusted sources
              </span>
            </div>
          </div>
          <button className="icon-button" type="button" onClick={resetChat} aria-label="Reset chat">
            <RotateCcw size={18} aria-hidden="true" />
          </button>
        </header>

        <div className="message-list" aria-live="polite">
          {messages.map((message) => (
            <article className={`message ${message.role}`} key={message.id}>
              <div className="message-label">{message.role === "assistant" ? "Harbor" : "You"}</div>
              <p>{message.content}</p>

              {message.role === "assistant" && <MetadataBadges metadata={message.metadata} />}

              {message.citations.length > 0 && (
                <ul className="citation-list" aria-label="Sources">
                  {message.citations.map((citation) => (
                    <li key={citation.url}>
                      <a href={citation.url} target="_blank" rel="noreferrer">
                        {citation.title}
                        <ExternalLink size={14} aria-hidden="true" />
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </article>
          ))}

          {isLoading && (
            <article className="message assistant loading">
              <div className="message-label">Harbor</div>
              <p>
                <LoaderCircle size={16} aria-hidden="true" />
                Planning answer
              </p>
            </article>
          )}
        </div>

        {error && <div className="error-banner">{error}</div>}

        <form className="composer" onSubmit={handleSubmit}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask about OHIP, health cards, Health811, or finding care in Ontario"
            rows={2}
            aria-label="Message Harbor"
          />
          <button className="send-button" type="submit" disabled={isLoading || input.trim().length === 0}>
            <ArrowUp size={18} aria-hidden="true" />
            <span>Send</span>
          </button>
        </form>

        <div className="starter-prompts" aria-label="Starter questions">
          {starterPrompts.map((prompt) => (
            <button type="button" key={prompt} onClick={() => usePrompt(prompt)}>
              {prompt}
            </button>
          ))}
        </div>
      </section>
    </main>
  );
}
