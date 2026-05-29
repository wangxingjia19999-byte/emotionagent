from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ==================== 量表定义 ====================

SCALES = {
    "daily_mood": {
        "name": "每日心情快评",
        "description": "4 道题快速了解今天的情绪状态",
        "instruction": "请根据今天的实际感受回答以下问题",
        "questions": [
            {"id": 1, "text": "今天我感到心情低落或沮丧", "options": ["完全没有", "有几天", "一半以上天数", "几乎每天"]},
            {"id": 2, "text": "今天我对事物缺乏兴趣或乐趣", "options": ["完全没有", "有几天", "一半以上天数", "几乎每天"]},
            {"id": 3, "text": "今天我感到紧张、焦虑或不安", "options": ["完全没有", "有几天", "一半以上天数", "几乎每天"]},
            {"id": 4, "text": "今天我能感受到生活中的温暖和美好", "options": ["几乎每天", "一半以上天数", "有几天", "完全没有"]},
        ],
        "scoring": {
            0: "良好", 3: "良好", 7: "轻度", 9: "中度", 12: "较重",
        },
    },
    "phq9": {
        "name": "PHQ-9 抑郁筛查量表",
        "description": "9 道题评估过去两周的抑郁状态（国际标准量表）",
        "instruction": "在过去两周里，你有多频繁被以下问题困扰？",
        "questions": [
            {"id": 1, "text": "做事时提不起劲或没有兴趣"},
            {"id": 2, "text": "感到心情低落、沮丧或绝望"},
            {"id": 3, "text": "入睡困难、睡不安稳或睡眠过多"},
            {"id": 4, "text": "感到疲倦或没有精力"},
            {"id": 5, "text": "食欲不振或吃得过多"},
            {"id": 6, "text": "觉得自己很糟，或觉得自己很失败，或让自己和家人失望"},
            {"id": 7, "text": "难以集中注意力做事情，如看手机或电视"},
            {"id": 8, "text": "说话或行动缓慢到别人都能察觉，或相反——烦躁、坐立不安"},
            {"id": 9, "text": "有不如死掉的念头，或以某种方式伤害自己"},
        ],
        "options": ["完全没有", "有几天", "一半以上天数", "几乎每天"],
        "scoring": {
            0: "无抑郁症状", 4: "轻度抑郁", 9: "中度抑郁", 14: "中重度抑郁", 19: "重度抑郁", 27: "极重度抑郁",
        },
    },
    "gad7": {
        "name": "GAD-7 焦虑筛查量表",
        "description": "7 道题评估过去两周的焦虑状态（国际标准量表）",
        "instruction": "在过去两周里，你有多频繁被以下问题困扰？",
        "questions": [
            {"id": 1, "text": "感到紧张、焦虑或烦躁"},
            {"id": 2, "text": "无法停止或控制担忧"},
            {"id": 3, "text": "对各种各样的事情过度担忧"},
            {"id": 4, "text": "很难放松下来"},
            {"id": 5, "text": "由于不安而无法静坐"},
            {"id": 6, "text": "变得容易烦恼或急躁"},
            {"id": 7, "text": "感到害怕，好像会发生可怕的事情"},
        ],
        "options": ["完全没有", "有几天", "一半以上天数", "几乎每天"],
        "scoring": {
            0: "无焦虑症状", 4: "轻度焦虑", 9: "中度焦虑", 14: "中重度焦虑", 21: "重度焦虑",
        },
    },
}


def calculate_score(scale_type: str, answers: list[int]) -> tuple[int, str]:
    """计算量表得分和等级"""
    scale = SCALES.get(scale_type)
    if not scale:
        return sum(answers), "未知"

    total = sum(answers)
    scoring: dict[int, str] = scale["scoring"]
    thresholds = sorted(scoring.keys())

    level = scoring[thresholds[-1]]
    for i, threshold in enumerate(thresholds):
        if total <= threshold:
            level = scoring[threshold]
            break

    return total, level


# ==================== Pydantic Schemas ====================


class QuestionnaireSubmit(BaseModel):
    scale_type: str = Field(..., description="量表类型: daily_mood / phq9 / gad7")
    answers: list[int] = Field(..., description="答案列表，每道题 0-3 分")

    class Config:
        json_schema_extra = {
            "example": {"scale_type": "daily_mood", "answers": [0, 1, 2, 1]}
        }


class QuestionnaireResult(BaseModel):
    scale_type: str
    total_score: int
    result_level: str
    max_score: int
    interpretation: str


class QuestionnaireHistoryItem(BaseModel):
    id: int
    scale_type: str
    scale_name: str
    answers: list[int]
    total_score: int
    result_level: str
    created_at: datetime


class QuestionnaireTrendPoint(BaseModel):
    date: str
    score: int
    level: str
    scale_type: str


class QuestionnairePageResponse(BaseModel):
    items: list[QuestionnaireHistoryItem]
    total: int
    page: int
    page_size: int


class QuestionnaireScaleInfo(BaseModel):
    key: str
    name: str
    description: str
    question_count: int
