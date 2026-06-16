from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.agent import (
    ChatRequest, ChatResponse, MultiAgentChatResponse,
    FacialExpressionRequest, FacialExpressionResponse,
    ExpressionSuggestionRequest, ExpressionSuggestionResponse,
)
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


@router.post("/facial-expression", response_model=FacialExpressionResponse)
def detect_facial_expression(
    payload: FacialExpressionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    面部表情检测端点 — 接收前端摄像头帧 (Base64 JPEG)，
    使用 MediaPipe Face Mesh 进行面部表情分类。

    返回检测到的表情标签、中文名称和置信度。
    同时将结果存入内存，供 Agent 工具 `get_current_facial_expression` 读取。
    """
    import base64
    import logging
    from agent.facial_expression import expression_detector, store_current_expression

    logger = logging.getLogger("app")

    if not payload.image_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image_base64 不能为空",
        )

    uid = payload.user_id or str(current_user.id)

    try:
        # 解码 Base64 图像
        # 可能带有 data:image/jpeg;base64, 前缀
        b64_data = payload.image_base64
        if "," in b64_data:
            b64_data = b64_data.split(",", 1)[1]
        image_bytes = base64.b64decode(b64_data)

        # 检测表情
        result = expression_detector.detect_from_bytes(image_bytes)

        if result is None:
            logger.info("facial_expression_no_face", extra={"user_id": uid})
            return FacialExpressionResponse(
                code=0,
                message="未检测到人脸",
                data=None,
            )

        # 存储结果供 Agent 工具读取
        store_current_expression(uid, result)

        logger.info(
            "facial_expression_detected",
            extra={
                "user_id": uid,
                "expression": result.label,
                "confidence": result.confidence,
            },
        )

        return FacialExpressionResponse(
            code=0,
            message="success",
            data={
                "label": result.label,
                "label_cn": result.label_cn,
                "confidence": result.confidence,
                "features": {
                    k: round(v, 4) if isinstance(v, (int, float)) else v
                    for k, v in result.features.items()
                },
            },
        )
    except Exception as e:
        logger.error(
            "facial_expression_error",
            extra={"error": str(e), "user_id": uid},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"表情检测失败: {str(e)}",
        )


@router.post("/expression-suggestion", response_model=ExpressionSuggestionResponse)
def get_expression_suggestion(
    payload: ExpressionSuggestionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    表情自动建议 — 摄像头检测到用户表情后自动触发。
    由前端 FacialExpressionDetector 在表情稳定变化时调用。
    AI 会结合检测到的表情给出个性化的情绪支持、鼓励或建议。
    """
    import logging
    logger = logging.getLogger("app")

    uid = str(current_user.id)

    # 情绪提示映射
    suggestion_prompts = {
        "happy": (
            "我看到你脸上露出了开心的笑容！嘴角上扬，看起来心情不错。"
            "请用一个温暖、真诚的语气回应，可以分享这份喜悦，"
            "也可以借机引导用户聊聊今天发生了什么好事，注意不要过于刻意。回复简短自然，2-4句话。"
        ),
        "sad": (
            "我注意到你看起来有些悲伤，我能感受到你的低落。"
            "请用温柔、共情的语气回应，先接纳情绪（不要否定或立刻鼓励），"
            "然后给一个开放式的邀请（比如'愿意和我聊聊吗'），让用户感到被理解和陪伴。回复2-4句话。"
        ),
        "surprised": (
            "你看起来有些惊讶！眉毛抬高、表情生动。"
            "请用好奇、轻松的语气回应，可以问用户是不是看到了什么有趣或意外的事情。"
            "回复简短有趣，2-3句话。"
        ),
        "angry": (
            "我注意到你看起来有些愤怒，眉头紧锁。"
            "请用平稳、温和的语气回应，先承认情绪是正常的（不要评判），"
            "给用户空间。可以邀请用户深呼吸或聊聊发生了什么。回复简短，2-3句话，语气要平和。"
        ),
        "fearful": (
            "你看起来有些紧张或不安，我能理解这种感受。"
            "请用安抚、安全的语气回应，传递'我在这里陪你'的信号。"
            "不要追问细节，先帮助用户感到安全。回复简短温暖，2-3句话。"
        ),
        "disgusted": (
            "你看起来有些不满或不舒服。"
            "请用关心、开放的语气回应，询问用户是否遇到了什么不愉快的事情。"
            "给用户表达的空间。回复简短，2-3句话。"
        ),
        "neutral": (
            "用户表情平静放松。"
            "请用一个自然、友好的方式打个招呼，问问用户今天想聊什么。"
            "回复简短轻松，1-2句话。"
        ),
    }

    prompt = suggestion_prompts.get(
        payload.expression,
        f"用户当前表情为: {payload.expression_cn or payload.expression}。请自然、温暖地回应，2-3句话。",
    )

    try:
        # 拼装一个内部触发消息，让多 Agent 系统处理
        trigger_message = (
            f"[系统提示] 摄像头自动检测到用户当前表情: {payload.expression_cn or payload.expression}。"
            f"{prompt}"
            f"请直接以心语陪伴的身份对用户说话，不要提及'检测到'或'系统提示'这些词。"
        )

        result = mcp_emotion_agent.chat_multi_agent(trigger_message, user_id=uid)

        logger.info(
            "expression_suggestion_generated",
            extra={
                "user_id": uid,
                "expression": payload.expression,
                "expression_cn": payload.expression_cn,
            },
        )

        return ExpressionSuggestionResponse(
            code=0,
            message="success",
            data={
                "reply": result.get("reply", ""),
                "expression": payload.expression,
                "expression_cn": payload.expression_cn,
                "agent_used": result.get("agent_used", "emotion_companion"),
                "crisis_detected": result.get("crisis_detected", False),
            },
        )
    except Exception as e:
        logger.error(
            "expression_suggestion_error",
            extra={"error": str(e), "user_id": uid},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"表情建议生成失败: {str(e)}",
        )
