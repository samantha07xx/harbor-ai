"""LLM answer generation boundary for grounded Harbor responses."""

from dataclasses import dataclass
from typing import Protocol

import httpx


@dataclass(frozen=True)
class LLMAnswerRequest:
    """Grounded answer generation request."""

    question: str
    intent: str
    evidence: list[str]


class LLMAnswerProvider(Protocol):
    """Protocol for answer generation providers."""

    model: str

    def generate_answer(self, request: LLMAnswerRequest) -> str:
        """Generate a grounded answer from retrieved evidence."""


class OpenAIAnswerProvider:
    """Answer provider backed by OpenAI's Responses API."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gpt-5-mini",
        base_url: str = "https://api.openai.com/v1",
        http_client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI answer generation")

        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._http_client = http_client

    def generate_answer(self, request: LLMAnswerRequest) -> str:
        """Generate a concise, cited answer using only trusted evidence."""

        response = self._client().post(
            f"{self.base_url}/responses",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "input": [
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "input_text",
                                "text": GROUNDED_ANSWER_SYSTEM_PROMPT,
                            }
                        ],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": build_grounded_answer_prompt(request),
                            }
                        ],
                    },
                ],
            },
        )
        response.raise_for_status()
        return extract_response_text(response.json()).strip()

    def _client(self) -> httpx.Client:
        """Return the configured HTTP client."""

        return self._http_client or httpx.Client(timeout=45.0)


GROUNDED_ANSWER_SYSTEM_PROMPT = (
    "You are Harbor, an Ontario healthcare navigation assistant. "
    "Answer only from the trusted source material provided in the prompt. Do not diagnose, "
    "prescribe, or invent facts. Give the user a direct, practical answer in no more than "
    "four concise bullets. Use clear labels in the same line, such as '- How to apply: ...'. "
    "Include citation markers like [1] for factual claims. Do not mention internal words "
    "like excerpts, chunks, retrieval, supplied material, or RAG. If the evidence is "
    "incomplete, briefly say what is missing and point the user to the cited official source."
)


def build_grounded_answer_prompt(request: LLMAnswerRequest) -> str:
    """Build the user prompt for grounded answer generation."""

    evidence = "\n\n".join(request.evidence)
    return "\n".join(
        [
            f"User question: {request.question}",
            f"Detected intent: {request.intent}",
            "",
            "Trusted source excerpts:",
            evidence,
            "",
            "Write a concise user-facing answer for someone navigating healthcare in Ontario.",
        ]
    )


def extract_response_text(body: dict) -> str:
    """Extract output text from an OpenAI Responses API response."""

    output_text = body.get("output_text")
    if isinstance(output_text, str) and output_text:
        return output_text

    text_parts: list[str] = []
    for output_item in body.get("output", []):
        for content_item in output_item.get("content", []):
            text = content_item.get("text")
            if isinstance(text, str):
                text_parts.append(text)
    return "\n".join(text_parts)
