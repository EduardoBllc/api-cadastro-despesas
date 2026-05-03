"""create_historico_preco_itens

Revision ID: c9d8e7f6a5b4
Revises: a4b7c1d2e3f5
Create Date: 2026-04-28 10:55:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9d8e7f6a5b4"
down_revision: Union[str, None] = "a4b7c1d2e3f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "historico_preco_itens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("item_despesa_id", sa.Uuid(), nullable=False),
        sa.Column("estabelecimento_id", sa.Uuid(), nullable=False),
        sa.Column("valor_unitario", sa.Numeric(precision=13, scale=2), nullable=False),
        sa.Column("data_despesa", sa.Date(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["estabelecimento_id"], ["estabelecimentos.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["item_despesa_id"], ["itens_despesa.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["itens.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_despesa_id"),
    )


def downgrade() -> None:
    op.drop_table("historico_preco_itens")
