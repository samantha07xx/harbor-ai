"""Chat API routes."""

from typing import Annotated

import httpx
from fastapi import APIRouter, Depends

from app.agent.react_agent import AgentTurnRequest, DeterministicHealthcareAgent
from app.api.dependencies import get_deterministic_healthcare_agent
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def create_chat_response(
    request: ChatRequest,
    agent: Annotated[
        DeterministicHealthcareAgent,
        Depends(get_deterministic_healthcare_agent),
    ],
) -> ChatResponse:
    """Return a deterministic pre-LLM agent response."""

    try:
        return agent.run_turn(
            AgentTurnRequest(
                session_id=request.session_id,
                message=request.message,
                user_context=request.user_context,
            )
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            return ChatResponse(
                answer=(
                    "Harbor reached the trusted-source pipeline, but OpenAI is currently "
                    "rate limiting this project. Wait a minute and try again, or check the "
                    "project's billing and rate limits before continuing."
                ),
                citations=[],
                suggested_followups=[
                    "How do I apply for OHIP?",
                    "What documents do I need for a health card?",
                    "Can I get care before OHIP?",
                ],
                metadata={
                    "session_id": request.session_id,
                    "implementation_status": "openai_rate_limited",
                    "provider_status_code": exc.response.status_code,
                    "user_context": request.user_context,
                },
            )
        raise
