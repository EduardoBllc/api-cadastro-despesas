"""create_tipos_estabelecimento

Revision ID: fa4a5df06c8e
Revises: 74ae6c528a7f
Create Date: 2026-04-28 10:15:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
import uuid

# revision identifiers, used by Alembic.
revision: str = "fa4a5df06c8e"
down_revision: Union[str, None] = "74ae6c528a7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tipos_estabelecimento",
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
    tipos = [
        "Supermercado",
        "Agropecuária",
        "Pet Shop",
        "Posto de Combustível",
        "Farmácia",
        "Restaurante",
        "Oficina",
        "Outros",
    ]
    for tipo in tipos:
        op.execute(
            f"INSERT INTO tipos_estabelecimento (id, descricao) VALUES ('{uuid.uuid4()}', '{tipo}')"
        )


def downgrade() -> None:
    op.drop_table("tipos_estabelecimento")
