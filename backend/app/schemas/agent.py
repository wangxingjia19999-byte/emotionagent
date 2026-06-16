from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    expression_trigger: Optional[str] = Field(
        None, description="当由表情检测自动触发时，传入表情标签 (如 happy/sad/angry)"
    )


class ExpressionSuggestionRequest(BaseModel):
    """表情自动建议请求 — 摄像头检测到表情后自动触发"""
    expression: str = Field(..., description="表情标签 (happy/sad/angry/fearful/surprised/disgusted/neutral)")
    expression_cn: str = Field("", description="表情中文名")


class ExpressionSuggestionResponse(BaseModel):
    """表情自动建议响应"""
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None


class ChatResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: dict


class FacialExpressionRequest(BaseModel):
    """面部表情检测请求 — 前端上传摄像头帧 (Base64 JPEG)"""
    image_base64: str = Field(..., description="Base64 编码的 JPEG 图像帧")
    user_id: Optional[str] = Field(None, description="用户 ID")


class FacialExpressionResponse(BaseModel):
    """面部表情检测响应"""
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None


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

