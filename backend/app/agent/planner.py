"""ReAct-style planning boundary for Harbor tool use."""

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol

import httpx

PLANNER_MAX_OUTPUT_TOKENS = 320


class AgentPlanRoute(StrEnum):
    """Planner routes for deciding whether to call retrieval."""

    RETRIEVE = "retrieve"
    CLARIFY = "clarify"
    DIRECT_ANSWER = "direct_answer"
    OUT_OF_SCOPE = "out_of_scope"
    SAFETY = "safety"


@dataclass(frozen=True)
class AgentPlanRequest:
    """Input to the ReAct-style planner."""

    message: str
    user_context: dict[str, Any]


@dataclass(frozen=True)
class AgentPlan:
    """Structured planner decision."""

    route: AgentPlanRoute
    message: str
    retrieval_question: str | None = None
    rationale: str | None = None


class AgentPlanner(Protocol):
    """Protocol for agent planners."""

    model: str

    def plan(self, request: AgentPlanRequest) -> AgentPlan:
        """Decide how the agent should handle one turn."""


class OpenAIReActPlanner:
    """OpenAI-backed planner that decides whether Harbor should call RAG."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gpt-5-mini",
        base_url: str = "https://api.openai.com/v1",
        http_client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI agent planning")

        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._http_client = http_client

    def plan(self, request: AgentPlanRequest) -> AgentPlan:
        """Call OpenAI to produce a structured tool-use plan."""

        response = self._client().post(
            f"{self.base_url}/responses",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "max_output_tokens": PLANNER_MAX_OUTPUT_TOKENS,
                "input": [
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "input_text",
                                "text": REACT_PLANNER_SYSTEM_PROMPT,
                            }
                        ],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": build_planner_prompt(request),
                            }
                        ],
                    },
                ],
            },
        )
        response.raise_for_status()
        response_text = extract_response_text(response.json())
        try:
            return parse_agent_plan(response_text)
        except (json.JSONDecodeError, ValueError):
            return AgentPlan(
                route=AgentPlanRoute.RETRIEVE,
                message="",
                retrieval_question=request.message,
                rationale="Planner output was not valid JSON; defaulting to trusted source lookup.",
            )

    def _client(self) -> httpx.Client:
        """Return the configured HTTP client."""

        return self._http_client or httpx.Client(timeout=30.0)


REACT_PLANNER_SYSTEM_PROMPT = (
    "You are Harbor's ReAct-style planner for Ontario healthcare navigation. "
    "Decide whether to call the healthcare_retrieval tool. Return JSON only. "
    "Use route 'retrieve' when answering requires current trusted Ontario "
    "healthcare source material such as OHIP, health cards, Health811, clinics, "
    "family doctors, or newcomer healthcare access. Use 'clarify' when the user "
    "is in scope but the request is too vague. Use 'direct_answer' only for "
    "simple conversational or capability questions that do not need source lookup. "
    "Use 'out_of_scope' for non-healthcare or non-Ontario navigation questions. "
    "Use 'safety' for urgent symptoms or emergency language. Do not include hidden "
    "chain-of-thought; the rationale field should be a short operational reason."
)


def build_planner_prompt(request: AgentPlanRequest) -> str:
    """Build the planner prompt."""

    return "\n".join(
        [
            f"User message: {request.message}",
            f"User context: {json.dumps(request.user_context, sort_keys=True)}",
            "",
            "Return exactly this JSON shape:",
            "{",
            '  "route": "retrieve | clarify | direct_answer | out_of_scope | safety",',
            '  "message": "short user-facing response if no tool is needed",',
            '  "retrieval_question": "optimized retrieval question when route is retrieve",',
            '  "rationale": "short operational reason"',
            "}",
        ]
    )


def parse_agent_plan(text: str) -> AgentPlan:
    """Parse planner JSON into an AgentPlan."""

    body = json.loads(extract_json_object(text))
    route = AgentPlanRoute(str(body["route"]))
    retrieval_question = body.get("retrieval_question")
    if not isinstance(retrieval_question, str) or not retrieval_question.strip():
        retrieval_question = None

    message = body.get("message")
    if not isinstance(message, str):
        message = ""

    rationale = body.get("rationale")
    if not isinstance(rationale, str):
        rationale = None

    return AgentPlan(
        route=route,
        message=message,
        retrieval_question=retrieval_question,
        rationale=rationale,
    )


def extract_json_object(text: str) -> str:
    """Extract a JSON object, tolerating fenced output."""

    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL)
    if fenced_match:
        return fenced_match.group(1)

    object_match = re.search(r"(\{.*\})", stripped, flags=re.DOTALL)
    if object_match:
        return object_match.group(1)

    raise ValueError("Planner response did not contain a JSON object")


def extract_response_text(body: dict) -> str:
    """Extract text from an OpenAI Responses API response."""

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
