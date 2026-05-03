"""create_despesas

Revision ID: 74aa58e8c94c
Revises: 2f8c811c1b06
Create Date: 2026-04-28 10:40:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "74aa58e8c94c"
down_revision: Union[str, None] = "2f8c811c1b06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "despesas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "data_despesa",
            sa.Date(),
            server_default=sa.text("CURRENT_DATE"),
            nullable=False,
        ),
        sa.Column("estabelecimento_id", sa.Uuid(), nullable=False),
        sa.Column("categoria_despesa_id", sa.Uuid(), nullable=False),
        sa.Column("valor_total", sa.Numeric(precision=13, scale=2), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["categoria_despesa_id"], ["categorias_despesa.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["estabelecimento_id"], ["estabelecimentos.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("despesas")
