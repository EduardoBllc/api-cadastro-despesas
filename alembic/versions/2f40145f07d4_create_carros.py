"""create_carros

Revision ID: 2f40145f07d4
Revises: fa4a5df06c8e
Create Date: 2026-04-28 10:20:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2f40145f07d4"
down_revision: Union[str, None] = "fa4a5df06c8e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "carros",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=60), nullable=False),
        sa.Column("placa", sa.String(length=8), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
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
        sa.UniqueConstraint("placa"),
    )


def downgrade() -> None:
    op.drop_table("carros")
