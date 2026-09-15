"""Chat API routes."""

from typing import Annotated

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

    return agent.run_turn(
        AgentTurnRequest(
            session_id=request.session_id,
            message=request.message,
            user_context=request.user_context,
        )
    )
