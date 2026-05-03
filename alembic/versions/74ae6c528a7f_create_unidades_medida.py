"""create_unidades_medida

Revision ID: 74ae6c528a7f
Revises: 7f8f225de1fd
Create Date: 2026-04-28 10:10:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
import uuid

# revision identifiers, used by Alembic.
revision: str = "74ae6c528a7f"
down_revision: Union[str, None] = "7f8f225de1fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "unidades_medida",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("descricao", sa.String(length=60), nullable=False),
        sa.Column(
            "data_cadastro",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "data_alteracao",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("descricao"),
    )

    # Seed inicial
    for unit in ["un", "kg", "L", "m", "cx", "pt"]:
        op.execute(
            f"INSERT INTO unidades_medida (id, descricao) VALUES ('{uuid.uuid4()}', '{unit}')"
        )


def downgrade() -> None:
    op.drop_table("unidades_medida")
