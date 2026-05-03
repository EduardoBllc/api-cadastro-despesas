"""create_itens_despesa

Revision ID: b6aabd68c89c
Revises: 74aa58e8c94c
Create Date: 2026-04-28 10:45:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b6aabd68c89c"
down_revision: Union[str, None] = "74aa58e8c94c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "itens_despesa",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("despesa_id", sa.Uuid(), nullable=False),
        sa.Column("item_id", sa.Uuid(), nullable=True),
        sa.Column("quantidade", sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column("valor_unitario", sa.Numeric(precision=13, scale=2), nullable=False),
        sa.Column(
            "valor_total",
            sa.Numeric(precision=13, scale=2),
            sa.Computed("quantidade * valor_unitario", persisted=True),
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(["despesa_id"], ["despesas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["itens.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("itens_despesa")
