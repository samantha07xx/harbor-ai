import { ArrowUp, ExternalLink, LoaderCircle, RotateCcw } from "lucide-react";
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
    content:
      "Welcome to Harbor. Ask a question about Ontario healthcare navigation and I will test the backend connection.",
    citations: [],
  },
];

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

              {message.suggestedFollowups && message.suggestedFollowups.length > 0 && (
                <div className="followups" aria-label="Suggested follow-up questions">
                  {message.suggestedFollowups.map((followup) => (
                    <button type="button" key={followup} onClick={() => usePrompt(followup)}>
                      {followup}
                    </button>
                  ))}
                </div>
              )}
            </article>
          ))}

          {isLoading && (
            <article className="message assistant loading">
              <div className="message-label">Harbor</div>
              <p>
                <LoaderCircle size={16} aria-hidden="true" />
                Checking the backend
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
