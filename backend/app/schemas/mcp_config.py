import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class MCPServerBase(BaseModel):
    name: str
    command: str
    args: Optional[str] = "[]"
    env_vars: Optional[str] = "{}"
    enabled: bool = True
    description: Optional[str] = None

    @field_validator("args")
    @classmethod
    def validate_args_json(cls, v: Optional[str]) -> str:
        if v is None:
            return "[]"
        try:
            json.loads(v)
        except json.JSONDecodeError:
            raise ValueError("args 必须是有效的 JSON 数组")
        return v

    @field_validator("env_vars")
    @classmethod
    def validate_env_json(cls, v: Optional[str]) -> str:
        if v is None:
            return "{}"
        try:
            parsed = json.loads(v)
            if not isinstance(parsed, dict):
                raise ValueError("env_vars 必须是 JSON 对象")
        except json.JSONDecodeError:
            raise ValueError("env_vars 必须是有效的 JSON 对象")
        return v


class MCPServerCreate(MCPServerBase):
    pass


class MCPServerUpdate(BaseModel):
    command: Optional[str] = None
    args: Optional[str] = None
    env_vars: Optional[str] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None


class MCPServerResponse(MCPServerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MCPToolInfo(BaseModel):
    name: str
    description: str
    source: str  # "builtin" 或 "mcp"


class MCPServerStatus(BaseModel):
    name: str
    command: str
    args: list[str]
    enabled: bool
    description: Optional[str]
    connected: bool
    tools_count: int
    has_env_keys: list[str]


class MCPTestResult(BaseModel):
    success: bool
    tools: Optional[list[dict]] = None
    error: Optional[str] = None


class MCPChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None


class MCPChatResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: dict
