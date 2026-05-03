"""create_itens

Revision ID: 04d24be09647
Revises: d29256352e26
Create Date: 2026-04-28 10:30:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "04d24be09647"
down_revision: Union[str, None] = "d29256352e26"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "itens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("descricao", sa.String(length=120), nullable=False),
        sa.Column("categoria_item_id", sa.Uuid(), nullable=False),
        sa.Column("unidade_medida_id", sa.Uuid(), nullable=True),
        sa.Column("valor_referencia", sa.Numeric(precision=13, scale=2), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
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
            ["categoria_item_id"], ["categorias_item.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["unidade_medida_id"], ["unidades_medida.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("itens")
