from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.agent import ChatRequest, ChatResponse, MultiAgentChatResponse
from app.schemas.mcp_config import MCPChatRequest, MCPChatResponse
from app.utils.jwt import get_current_user
from agent import emotion_agent_service
from agent.mcp_agent import mcp_emotion_agent

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(payload: ChatRequest):
    """基础版 Agent 对话（RAG 管道）"""
    if not payload.message.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="消息不能为空")

    try:
        reply = emotion_agent_service.chat(payload.message)
        return ChatResponse(
            code=0,
            message="success",
            data={"reply": reply}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent 处理异常: {str(e)}"
        )


@router.post("/chat/enhanced", response_model=MCPChatResponse)
def chat_with_enhanced_agent(
    payload: MCPChatRequest,
    current_user: User = Depends(get_current_user),
):
    """增强版 Agent 对话（RAG + MCP 工具）"""
    if not payload.message.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="消息不能为空")

    try:
        uid = payload.user_id or str(current_user.id)
        reply = mcp_emotion_agent.chat(payload.message, user_id=uid)
        return MCPChatResponse(
            code=0,
            message="success",
            data={"reply": reply, "user_id": uid}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent 处理异常: {str(e)}"
        )


@router.post("/chat/multi", response_model=MultiAgentChatResponse)
def chat_with_multi_agent(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    多 Agent 对话（Supervisor 架构）

    由 Supervisor 自动路由到:
    - emotion_companion: 情绪陪伴、RAG 检索、画像分析
    - shopping_advisor: 商城浏览、商品推荐

    同时进行危机信号预检测。
    """
    if not payload.message.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="消息不能为空")

    try:
        uid = str(current_user.id)
        result = mcp_emotion_agent.chat_multi_agent(payload.message, user_id=uid)
        return MultiAgentChatResponse(
            code=0,
            message="success",
            data=result,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-Agent 处理异常: {str(e)}"
        )


@router.get("/tools")
def get_agent_tools():
    """获取 Agent 所有可用工具列表"""
    return {
        "code": 0,
        "message": "success",
        "data": mcp_emotion_agent.get_tools_info(),
    }


@router.get("/tools/multi")
def get_multi_agent_tools():
    """获取多 Agent 系统工具信息"""
    from agent.multi_agent import multi_agent
    return {
        "code": 0,
        "message": "success",
        "data": multi_agent.tools_info(),
    }
