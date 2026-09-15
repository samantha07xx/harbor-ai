"""Chat request and response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat request from the Harbor web UI."""

    session_id: str | None = Field(default=None, description="Optional client session ID.")
    message: str = Field(min_length=1, description="User's healthcare navigation question.")
    user_context: dict[str, Any] = Field(default_factory=dict)


class Citation(BaseModel):
    """Source citation returned with grounded answers."""

    title: str
    url: str


class ChatResponse(BaseModel):
    """Chat response returned to the frontend."""

    answer: str
    citations: list[Citation] = Field(default_factory=list)
    suggested_followups: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
