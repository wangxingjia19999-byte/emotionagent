from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserRegister(BaseModel):
    username: str = Field(min_length=1)
    email: str
    password: str = Field(min_length=6)
    nickname: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("用户名不能为空")
        return value

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
        if len(value) < 6:
            raise ValueError("密码长度不能少于6位")
        return value


class UserLogin(BaseModel):
    username: str
    password: str = Field(min_length=6)
    role: Optional[str] = None


class ProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str


class LoginResponseData(BaseModel):
    token: str
    user: UserResponse
