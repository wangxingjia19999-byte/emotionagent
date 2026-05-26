from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HomeUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nickname: str = ""
    avatar: str = ""
    username: str
    email: str = ""
    occupation: str = ""
    age: Optional[int] = None
    gender: str = ""
    role: str = ""


class HomeStatistics(BaseModel):
    ai_chat_count: int = 0
    friend_count: int = 0
    post_count: int = 0
    favorite_count: int = 0
    unread_private_message_count: int = 0


class HomeRecentAiSession(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    updated_at: Optional[str] = None


class HomeRecentPost(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: str = ""
    like_count: int = 0
    comment_count: int = 0


class HomeOverviewData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: HomeUser
    statistics: HomeStatistics
    recent_ai_session: Optional[HomeRecentAiSession] = None
    recent_posts: list[HomeRecentPost] = Field(default_factory=list)