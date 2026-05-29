import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.questionnaire import QuestionnaireRecord
from app.models.user import User
from app.schemas.questionnaire import (
    SCALES,
    QuestionnaireHistoryItem,
    QuestionnairePageResponse,
    QuestionnaireResult,
    QuestionnaireScaleInfo,
    QuestionnaireSubmit,
    QuestionnaireTrendPoint,
    calculate_score,
)
from app.utils.jwt import get_current_user

router = APIRouter(prefix="/questionnaires", tags=["情绪问卷"])


def _scale_name(scale_type: str) -> str:
    scale = SCALES.get(scale_type)
    return scale["name"] if scale else scale_type


INTERPRETATIONS = {
    "daily_mood": {
        "良好": "今天的情绪状态不错，继续保持哦。",
        "轻度": "今天稍微有些低落，不妨做一件让自己开心的小事。",
        "中度": "今天情绪有些沉重，可以和信任的人聊一聊，或者来做一次 AI 陪伴对话。",
        "较重": "今天承受了不小的情绪压力，记得你不需要独自撑着，我随时在这里陪你。",
    },
    "phq9": {
        "无抑郁症状": "目前的情绪状态良好，未发现明显的抑郁症状。",
        "轻度抑郁": "存在轻度的抑郁情绪，适当运动、社交和专业倾诉都可能有所帮助。",
        "中度抑郁": "存在中度的抑郁症状，建议规律作息，并可以考虑寻求专业心理咨询。",
        "中重度抑郁": "抑郁症状较为明显，强烈建议寻求专业心理医生的帮助。你不是一个人在战斗。",
        "重度抑郁": "请尽快联系专业心理医生或拨打心理援助热线 400-161-9995。你的感受是真实且重要的。",
        "极重度抑郁": "请尽快联系专业心理医生或拨打心理援助热线 400-161-9995。世界上有人愿意听你说，请不要独自承担。",
    },
    "gad7": {
        "无焦虑症状": "目前的焦虑水平在正常范围内，无需担心。",
        "轻度焦虑": "有一些轻度的焦虑情绪，可以尝试深呼吸、正念冥想来缓解。",
        "中度焦虑": "焦虑水平有所升高，如果持续困扰可以找信任的人聊聊或寻求专业帮助。",
        "中重度焦虑": "焦虑症状比较明显，建议考虑专业的心理咨询或治疗。",
        "重度焦虑": "请尽快寻求专业心理医生的帮助，同时可以拨打心理援助热线 400-161-9995。",
    },
}


def _get_interpretation(scale_type: str, level: str) -> str:
    interps = INTERPRETATIONS.get(scale_type, {})
    return interps.get(level, "请结合其他评估和专业意见综合判断。")


# ==================== 量表信息 ====================


@router.get("/scales")
def list_scales():
    """获取可用量表列表"""
    scales_list = [
        QuestionnaireScaleInfo(
            key=key,
            name=info["name"],
            description=info["description"],
            question_count=len(info["questions"]),
        ).model_dump()
        for key, info in SCALES.items()
    ]
    return {"code": 0, "message": "success", "data": scales_list}


@router.get("/scales/{scale_type}")
def get_scale_detail(scale_type: str):
    """获取量表详情（题目和选项）"""
    scale = SCALES.get(scale_type)
    if not scale:
        return {"code": 1, "message": "未知量表类型"}
    return {"code": 0, "message": "success", "data": scale}


# ==================== 提交问卷 ====================


@router.post("/submit", status_code=status.HTTP_201_CREATED)
def submit_questionnaire(
    payload: QuestionnaireSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """提交问卷答案"""
    scale = SCALES.get(payload.scale_type)
    if not scale:
        return {"code": 1, "message": "未知量表类型"}

    expected_count = len(scale["questions"])
    if len(payload.answers) != expected_count:
        return {"code": 1, "message": f"该量表需要 {expected_count} 道题的答案，收到了 {len(payload.answers)} 道"}

    # 校验每道题答案在有效范围内
    for i, answer in enumerate(payload.answers):
        if answer < 0 or answer > 3:
            return {"code": 1, "message": f"第 {i+1} 题答案必须在 0-3 之间"}

    total_score, result_level = calculate_score(payload.scale_type, payload.answers)
    max_score = expected_count * 3

    record = QuestionnaireRecord(
        user_id=current_user.id,
        scale_type=payload.scale_type,
        answers=json.dumps(payload.answers, ensure_ascii=False),
        total_score=total_score,
        result_level=result_level,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    result = QuestionnaireResult(
        scale_type=payload.scale_type,
        total_score=total_score,
        result_level=result_level,
        max_score=max_score,
        interpretation=_get_interpretation(payload.scale_type, result_level),
    )
    return {"code": 0, "message": "提交成功", "data": result.model_dump()}


# ==================== 历史记录 ====================


@router.get("/history")
def get_questionnaire_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    scale_type: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取问卷历史记录"""
    query = db.query(QuestionnaireRecord).filter(
        QuestionnaireRecord.user_id == current_user.id
    )

    if scale_type:
        query = query.filter(QuestionnaireRecord.scale_type == scale_type)

    total = query.count()
    records = (
        query.order_by(QuestionnaireRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for r in records:
        try:
            answers = json.loads(r.answers)
        except json.JSONDecodeError:
            answers = []
        items.append(
            QuestionnaireHistoryItem(
                id=r.id,
                scale_type=r.scale_type,
                scale_name=_scale_name(r.scale_type),
                answers=answers,
                total_score=r.total_score,
                result_level=r.result_level,
                created_at=r.created_at,
            )
        )

    return {
        "code": 0,
        "message": "success",
        "data": QuestionnairePageResponse(
            items=items, total=total, page=page, page_size=page_size
        ).model_dump(),
    }


# ==================== 情绪趋势 ====================


@router.get("/trends")
def get_emotion_trends(
    days: int = Query(default=30, ge=7, le=365),
    scale_type: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取情绪趋势数据（用于图表）"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    query = db.query(QuestionnaireRecord).filter(
        QuestionnaireRecord.user_id == current_user.id,
        QuestionnaireRecord.created_at >= cutoff,
    )

    if scale_type:
        query = query.filter(QuestionnaireRecord.scale_type == scale_type)

    records = query.order_by(QuestionnaireRecord.created_at.asc()).all()

    trend_points = []
    for r in records:
        trend_points.append(
            QuestionnaireTrendPoint(
                date=r.created_at.strftime("%m-%d"),
                score=r.total_score,
                level=r.result_level,
                scale_type=r.scale_type,
            ).model_dump()
        )

    return {"code": 0, "message": "success", "data": trend_points}


# ==================== 今日是否已打卡 ====================


@router.get("/today-status")
def get_today_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """检查今天的打卡状态"""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    records = (
        db.query(QuestionnaireRecord)
        .filter(
            QuestionnaireRecord.user_id == current_user.id,
            QuestionnaireRecord.created_at >= today_start,
        )
        .all()
    )

    completed = list(set(r.scale_type for r in records))
    return {
        "code": 0,
        "message": "success",
        "data": {
            "completed_scales": completed,
            "total_scales": len(SCALES),
            "all_completed": len(completed) >= len(SCALES),
        },
    }
