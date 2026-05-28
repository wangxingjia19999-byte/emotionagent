import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_password_strength(value: str) -> str:
    """密码强度：至少8位，必须包含字母和数字"""
    if len(value) < 8:
        raise ValueError("密码长度不能少于8位")
    if not re.search(r"[a-zA-Z]", value):
        raise ValueError("密码必须包含至少一个字母")
    if not re.search(r"\d", value):
        raise ValueError("密码必须包含至少一个数字")
    return value


class SendVerifyCodeRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("邮箱不能为空")
        if "@" not in value or "." not in value:
            raise ValueError("邮箱格式不正确")
        return value


class UserRegister(BaseModel):
    email: str
    verification_code: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=6)
    nickname: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("邮箱不能为空")
        if "@" not in value or "." not in value:
            raise ValueError("邮箱格式不正确")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return _validate_password_strength(value)


class UserLogin(BaseModel):
    account: str = Field(min_length=1, description="邮箱或系统账号")
    password: str = Field(min_length=6)
    role: Optional[str] = None


class ProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    occupation: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=150)
    gender: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_profile_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("邮箱不能为空")
        if "@" not in value or "." not in value:
            raise ValueError("邮箱格式不正确")
        return value

    @field_validator("occupation")
    @classmethod
    def validate_occupation(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        return value or None

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if value and value not in {"male", "female", "other", "unknown"}:
            raise ValueError("性别值不合法")
        return value or None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)
    confirm_password: str = Field(min_length=6)

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, value: str) -> str:
        return _validate_password_strength(value)

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("密码长度不能少于8位")
        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    occupation: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    role: str


class LoginResponseData(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str
