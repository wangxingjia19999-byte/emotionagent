from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: dict


class MultiAgentChatResponse(BaseModel):
    """多 Agent 对话响应"""
    code: int = 0
    message: str = "success"
    data: dict = Field(
        default_factory=lambda: {
            "reply": "",
            "agent_used": "supervisor",
            "crisis_detected": False,
        }
    )

