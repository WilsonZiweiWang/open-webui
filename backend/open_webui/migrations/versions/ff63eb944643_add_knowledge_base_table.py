"""Add knowledge_base table

Revision ID: ff63eb944643
Revises: 49a73a23aa60
Create Date: 2024-10-07 18:21:51.681377

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.apps.webui.internal.db


# revision identifiers, used by Alembic.
revision: str = 'ff63eb944643'
down_revision: Union[str, None] = '49a73a23aa60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "knowledge_base",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_by_user_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("embedding_model", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("documents", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now(),),
    )


def downgrade() -> None:
    op.drop_table("knowledge_base")