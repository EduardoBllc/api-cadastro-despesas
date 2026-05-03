"""create_estabelecimentos

Revision ID: d29256352e26
Revises: 2f40145f07d4
Create Date: 2026-04-28 10:25:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d29256352e26"
down_revision: Union[str, None] = "2f40145f07d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "estabelecimentos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("descricao", sa.String(length=100), nullable=False),
        sa.Column("tipo_id", sa.Uuid(), nullable=False),
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
            ["tipo_id"], ["tipos_estabelecimento.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("estabelecimentos")
