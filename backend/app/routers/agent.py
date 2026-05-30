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


@router.get("/sessions")
def get_chat_sessions(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取当前用户的 AI 聊天历史会话列表。
    按时间倒序排列，支持分页。
    """
    from app.models.ai_chat_session import AiChatSession

    total = (
        db.query(AiChatSession)
        .filter(AiChatSession.user_id == current_user.id)
        .count()
    )

    sessions = (
        db.query(AiChatSession)
        .filter(AiChatSession.user_id == current_user.id)
        .order_by(AiChatSession.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for s in sessions:
        items.append({
            "id": s.id,
            "title": s.title or "未命名对话",
            "agent_used": s.agent_used,
            "crisis_detected": s.crisis_detected == 1,
            "first_message": s.first_message[:100] if s.first_message else "",
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "",
        })

    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/sessions/{session_id}")
def get_chat_session_detail(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取单个 AI 聊天会话的详细信息，包含完整对话消息。
    """
    import json
    from app.models.ai_chat_session import AiChatSession

    session = (
        db.query(AiChatSession)
        .filter(
            AiChatSession.id == session_id,
            AiChatSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # 解析 messages_json
    messages = []
    if session.messages_json:
        try:
            messages = json.loads(session.messages_json)
        except json.JSONDecodeError:
            messages = [
                {"role": "user", "content": session.first_message or ""},
                {"role": "assistant", "content": session.last_message or ""},
            ]

    return {
        "code": 0,
        "message": "success",
        "data": {
            "id": session.id,
            "title": session.title or "未命名对话",
            "agent_used": session.agent_used,
            "crisis_detected": session.crisis_detected == 1,
            "messages": messages,
            "created_at": session.created_at.strftime("%Y-%m-%d %H:%M") if session.created_at else "",
        },
    }
