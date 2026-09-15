"""Chat API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.agent.tools import HealthcareRetrievalTool
from app.api.dependencies import (
    get_healthcare_retrieval_tool,
    get_safety_policy,
)
from app.safety.policy import SafetyPolicy
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def create_chat_response(
    request: ChatRequest,
    retrieval_tool: Annotated[
        HealthcareRetrievalTool,
        Depends(get_healthcare_retrieval_tool),
    ],
    safety_policy: Annotated[SafetyPolicy, Depends(get_safety_policy)],
) -> ChatResponse:
    """Return a safety-gated pre-agent local RAG response."""

    safety_assessment = safety_policy.assess(request.message)
    if not safety_assessment.should_continue:
        return ChatResponse(
            answer=str(safety_assessment.message),
            citations=[],
            suggested_followups=[
                "How do I apply for OHIP?",
                "What documents do I need for a health card?",
                "Can I call Health811 for non-emergency advice?",
            ],
            metadata={
                "session_id": request.session_id,
                "implementation_status": "safety_layer",
                "safety_route": safety_assessment.route,
                "user_context": request.user_context,
            },
        )

    tool_result = retrieval_tool.run(request.message, limit=1)
    return ChatResponse(
        answer=tool_result.answer,
        citations=tool_result.citations,
        suggested_followups=[
            "How do I apply for OHIP?",
            "What documents do I need for a health card?",
            "Can I get care before OHIP?",
        ],
        metadata={
            "session_id": request.session_id,
            "implementation_status": "pre_agent_local_rag",
            "safety_route": safety_assessment.route,
            "tool_name": tool_result.tool_name,
            **tool_result.metadata,
            "user_context": request.user_context,
        },
    )
