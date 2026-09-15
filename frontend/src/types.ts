export type Citation = {
  title: string;
  url: string;
};

export type ChatRequest = {
  session_id: string;
  message: string;
  user_context: {
    province: "Ontario";
  };
};

export type ChatResponse = {
  answer: string;
  citations: Citation[];
  suggested_followups: string[];
  metadata: Record<string, unknown>;
};

export type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  content: string;
  citations: Citation[];
  metadata?: Record<string, unknown>;
  suggestedFollowups?: string[];
};
