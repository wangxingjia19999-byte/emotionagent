import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.mcp_config import MCPConfig
from app.models.user import User
from app.schemas.mcp_config import (
    MCPServerCreate,
    MCPServerResponse,
    MCPServerStatus,
    MCPServerUpdate,
    MCPTestResult,
    MCPToolInfo,
)
from app.utils.jwt import get_current_user
from agent.mcp_agent import mcp_emotion_agent
from agent.mcp_manager import MCPServerConfig, mcp_manager

router = APIRouter(prefix="/mcp", tags=["MCP管理"])


def _require_admin(user: User) -> None:
    if user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可操作 MCP 配置")


def _db_to_manager_config(db_config: MCPConfig) -> MCPServerConfig:
    """将数据库配置转换为 MCP Manager 配置"""
    args = json.loads(db_config.args) if db_config.args else []
    env_vars = json.loads(db_config.env_vars) if db_config.env_vars else {}
    return MCPServerConfig(
        name=db_config.name,
        command=db_config.command,
        args=args,
        env=env_vars,
        enabled=db_config.enabled,
        description=db_config.description or "",
    )


def _sync_manager_from_db(db: Session) -> None:
    """从数据库同步配置到 MCP Manager"""
    db_configs = db.query(MCPConfig).filter(MCPConfig.enabled == True).all()
    for cfg in db_configs:
        mcp_manager.configure_server(_db_to_manager_config(cfg))


# ==================== MCP 配置 CRUD ====================


@router.get("/servers", response_model=list[MCPServerResponse])
def list_mcp_servers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取所有 MCP 服务器配置列表（管理员）"""
    _require_admin(current_user)
    return db.query(MCPConfig).order_by(MCPConfig.id.asc()).all()


@router.post("/servers", response_model=MCPServerResponse, status_code=status.HTTP_201_CREATED)
def create_mcp_server(
    payload: MCPServerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """新增 MCP 服务器配置（管理员）"""
    _require_admin(current_user)

    existing = db.query(MCPConfig).filter(MCPConfig.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"服务器 '{payload.name}' 已存在")

    cfg = MCPConfig(**payload.model_dump())
    db.add(cfg)
    db.commit()
    db.refresh(cfg)

    # 同步到 MCP Manager
    mcp_manager.configure_server(_db_to_manager_config(cfg))
    return cfg


@router.put("/servers/{server_id}", response_model=MCPServerResponse)
def update_mcp_server(
    server_id: int,
    payload: MCPServerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新 MCP 服务器配置（管理员）"""
    _require_admin(current_user)

    cfg = db.query(MCPConfig).filter(MCPConfig.id == server_id).first()
    if not cfg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP 配置不存在")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cfg, field, value)

    db.commit()
    db.refresh(cfg)

    # 同步到 MCP Manager
    mcp_manager.configure_server(_db_to_manager_config(cfg))
    return cfg


@router.delete("/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mcp_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除 MCP 服务器配置（管理员）"""
    _require_admin(current_user)

    cfg = db.query(MCPConfig).filter(MCPConfig.id == server_id).first()
    if not cfg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP 配置不存在")

    mcp_manager.remove_server(cfg.name)
    db.delete(cfg)
    db.commit()


# ==================== MCP 工具与状态 ====================


@router.get("/tools", response_model=list[MCPToolInfo])
def list_all_tools(current_user: User = Depends(get_current_user)):
    """获取 Agent 当前所有可用工具（内置 + MCP）"""
    return mcp_emotion_agent.get_tools_info()


@router.get("/status", response_model=list[MCPServerStatus])
def get_mcp_status(current_user: User = Depends(get_current_user)):
    """获取所有 MCP 服务器连接状态（管理员）"""
    _require_admin(current_user)
    return mcp_manager.list_servers()


@router.post("/servers/{server_id}/test", response_model=MCPTestResult)
async def test_mcp_connection(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """测试 MCP 服务器连接（管理员）"""
    _require_admin(current_user)

    cfg = db.query(MCPConfig).filter(MCPConfig.id == server_id).first()
    if not cfg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP 配置不存在")

    # 先注册配置到管理器
    mcp_manager.configure_server(_db_to_manager_config(cfg))

    result = await mcp_manager.test_connection(cfg.name)
    return result


# ==================== MCP 预设配置 ====================


@router.get("/presets")
def list_preset_servers(current_user: User = Depends(get_current_user)):
    """获取系统预设的 MCP 服务器推荐列表"""
    _require_admin(current_user)

    from agent.mcp_manager import PRESET_MCP_SERVERS
    return PRESET_MCP_SERVERS


@router.post("/presets/load", status_code=status.HTTP_201_CREATED)
def load_presets_to_db(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """将预设 MCP 服务器配置导入数据库（管理员，去重）"""
    _require_admin(current_user)

    from agent.mcp_manager import PRESET_MCP_SERVERS

    created = []
    for preset in PRESET_MCP_SERVERS:
        existing = db.query(MCPConfig).filter(MCPConfig.name == preset["name"]).first()
        if existing:
            continue
        cfg = MCPConfig(
            name=preset["name"],
            command=preset["command"],
            args=json.dumps(preset["args"]),
            env_vars=json.dumps(preset["env"]),
            enabled=preset["enabled"],
            description=preset["description"],
        )
        db.add(cfg)
        created.append(preset["name"])

    db.commit()
    return {"imported": created, "count": len(created)}
