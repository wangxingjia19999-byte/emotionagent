from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, Text, func

from app.database import Base


class MCPConfig(Base):
    """MCP 服务器配置持久化模型"""

    __tablename__ = "mcp_configs"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    command = Column(String(200), nullable=False)
    args = Column(Text, nullable=True, comment="JSON 数组格式的参数列表")
    env_vars = Column(Text, nullable=True, comment="JSON 对象格式的环境变量")
    enabled = Column(Boolean, nullable=False, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
