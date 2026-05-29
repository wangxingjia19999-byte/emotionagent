"""initial_schema

Revision ID: 888d0aa5d3d2
Revises:
Create Date: 2026-05-27 20:08:21.160272

"""
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '888d0aa5d3d2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_SQL_FILE = Path(__file__).resolve().parents[2] / "sql" / "init_all_tables.sql"


def _iter_statements(sql_text: str):
    buffer: list[str] = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        upper = stripped.upper()
        if upper.startswith("CREATE DATABASE") or upper.startswith("USE "):
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            statement = "\n".join(buffer).strip()
            if statement.endswith(";"):
                statement = statement[:-1]
            if statement:
                yield statement
            buffer = []


def upgrade() -> None:
    """Upgrade schema to the current full database structure."""
    sql_text = _SQL_FILE.read_text(encoding="utf-8")
    for statement in _iter_statements(sql_text):
        op.execute(sa.text(statement))


def downgrade() -> None:
    """Downgrade schema."""
    for table_name in [
        "order_items",
        "orders",
        "user_addresses",
        "cart_items",
        "products",
        "product_categories",
        "mcp_configs",
        "verification_codes",
        "audit_logs",
        "crisis_alerts",
        "questionnaire_records",
        "private_messages",
        "friendships",
        "friend_requests",
        "emotion_logs",
        "favorites",
        "hugs",
        "likes",
        "comments",
        "posts",
        "admins",
        "user_profiles",
        "users",
    ]:
        op.execute(sa.text(f"DROP TABLE IF EXISTS {table_name}"))
