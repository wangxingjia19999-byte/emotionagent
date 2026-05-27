from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ==================== 用户搜索 ====================


class UserSearchItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str = ""
    avatar: str = ""
    occupation: Optional[str] = None
    is_friend: bool = False
    has_pending_request: bool = False


# ==================== 好友申请 ====================


class FriendRequestSend(BaseModel):
    to_user_id: int
    message: Optional[str] = Field(default=None, max_length=200)


class FriendRequestItem(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    message: Optional[str] = None
    status: str
    from_user: dict
    created_at: datetime


class FriendRequestList(BaseModel):
    items: list[FriendRequestItem]
    total: int


# ==================== 好友 ====================


class FriendItem(BaseModel):
    id: int  # friendship id
    friend_id: int
    username: str
    nickname: str = ""
    avatar: str = ""
    occupation: Optional[str] = None
    unread_count: int = 0
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    created_at: datetime


class FriendList(BaseModel):
    items: list[FriendItem]
    total: int


# ==================== 私聊消息 ====================


class PrivateMessageSend(BaseModel):
    receiver_id: int
    content: str = Field(min_length=1, max_length=2000)


class PrivateMessageItem(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime


class MessageHistory(BaseModel):
    items: list[PrivateMessageItem]
    total: int
    page: int
    page_size: int


class UnreadCount(BaseModel):
    total: int
    by_friend: dict
