"""Add chat_profile table

Revision ID: 49a73a23aa60
Revises: ca81bd47c050
Create Date: 2024-10-07 15:41:40.746087

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.apps.webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '49a73a23aa60'
down_revision: Union[str, None] = 'ca81bd47c050'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_profile",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_by_user_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("llm_model", sa.String(), nullable=False),
        sa.Column("roles_allowed", sa.String(), nullable=False),
        sa.Column("knowledge_bases", sa.String(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("params", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now(),),
    )


def downgrade() -> None:
    op.drop_table("chat_profile")
