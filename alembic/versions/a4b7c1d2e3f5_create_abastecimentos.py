"""create_abastecimentos

Revision ID: a4b7c1d2e3f5
Revises: b6aabd68c89c
Create Date: 2026-04-28 10:50:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a4b7c1d2e3f5"
down_revision: Union[str, None] = "b6aabd68c89c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "abastecimentos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("despesa_id", sa.Uuid(), nullable=False),
        sa.Column("carro_id", sa.Uuid(), nullable=False),
        sa.Column("posto_id", sa.Uuid(), nullable=True),
        sa.Column(
            "data_abastecimento",
            sa.Date(),
            server_default=sa.text("CURRENT_DATE"),
            nullable=False,
        ),
        sa.Column("quilometragem", sa.Integer(), nullable=False),
        sa.Column("litros", sa.Numeric(precision=9, scale=3), nullable=False),
        sa.Column("observacao", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["carro_id"], ["carros.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["despesa_id"], ["despesas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["posto_id"], ["estabelecimentos.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("despesa_id"),
    )


def downgrade() -> None:
    op.drop_table("abastecimentos")
