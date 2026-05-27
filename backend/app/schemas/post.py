from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


ALLOWED_POST_CATEGORIES = {
    "情绪倾诉",
    "学习生活",
    "人际关系",
    "校园日常",
    "其他",
}

ALLOWED_MOOD_TAGS = {
    "开心", "难过", "焦虑", "愤怒", "温暖",
    "平静", "孤独", "恐惧", "惊讶", "感激",
}


class PostAuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str = ""
    avatar: str = ""
    role: str = ""


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    category: Optional[str] = Field(default="其他", max_length=50)
    mood_tag: Optional[str] = Field(default=None, max_length=30)
    is_anonymous: bool = False
    image_url: Optional[str] = Field(default=None, max_length=255)
    image_urls: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("标题不能为空")
        if len(value) > 100:
            raise ValueError("标题长度不能超过100个字符")
        return value

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("正文不能为空")
        return value

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return "其他"
        value = value.strip()
        if not value:
            return "其他"
        if len(value) > 50:
            raise ValueError("分类长度不能超过50个字符")
        if value not in ALLOWED_POST_CATEGORIES:
            raise ValueError("分类不合法")
        return value

    @field_validator("image_urls")
    @classmethod
    def validate_image_urls(cls, value: list[str]) -> list[str]:
        cleaned_urls = [item.strip() for item in value if isinstance(item, str) and item.strip()]
        if len(cleaned_urls) > 9:
            raise ValueError("最多只能上传9张图片")
        return cleaned_urls


class PostUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=100)
    content: Optional[str] = None
    category: Optional[str] = Field(default=None, max_length=50)
    mood_tag: Optional[str] = Field(default=None, max_length=30)
    is_anonymous: Optional[bool] = None
    image_url: Optional[str] = Field(default=None, max_length=255)
    image_urls: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("标题不能为空")
        if len(value) > 100:
            raise ValueError("标题长度不能超过100个字符")
        return value

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("正文不能为空")
        return value

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("分类不能为空")
        if len(value) > 50:
            raise ValueError("分类长度不能超过50个字符")
        if value not in ALLOWED_POST_CATEGORIES:
            raise ValueError("分类不合法")
        return value

    @field_validator("image_urls")
    @classmethod
    def validate_image_urls(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        if value is None:
            return value
        cleaned_urls = [item.strip() for item in value if isinstance(item, str) and item.strip()]
        if len(cleaned_urls) > 9:
            raise ValueError("最多只能上传9张图片")
        return cleaned_urls


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("评论内容不能为空")
        return value


class CommentAuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str = ""
    avatar: str = ""
    role: str = ""


class PostItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    content: str
    category: str = "其他"
    mood_tag: Optional[str] = None
    is_anonymous: bool = False
    image_url: Optional[str] = None
    image_urls: list[str] = Field(default_factory=list)
    view_count: int = 0
    like_count: int = 0
    hug_count: int = 0
    comment_count: int = 0
    favorite_count: int = 0
    created_at: datetime
    updated_at: datetime
    author: PostAuthorResponse


class PostDetailResponse(PostItemResponse):
    liked: bool = False
    hugged: bool = False
    favorited: bool = False


class PostPageResponse(BaseModel):
    items: list[PostItemResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10


class CommentItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    author: CommentAuthorResponse


class CommentPageResponse(BaseModel):
    items: list[CommentItemResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10


class PostActionResponse(BaseModel):
    post_id: int
    liked: bool = False
    favorited: bool = False
    like_count: int = 0
    favorite_count: int = 0


class CommentActionResponse(BaseModel):
    comment_id: int
    post_id: int
