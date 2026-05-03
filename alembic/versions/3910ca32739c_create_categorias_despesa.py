"""create_categorias_despesa

Revision ID: 3910ca32739c
Revises: 
Create Date: 2026-04-28 10:00:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
import uuid

# revision identifiers, used by Alembic.
revision: str = "3910ca32739c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categorias_despesa",
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
    )

    categorias_despesa = [
        "Supermercado",
        "Restaurante",
        "Delivery de Comida",
        "Farmácia",
        "Combustível",
        "Transporte",
        "Consulta Médica e Exames",
        "Educação",
        "Serviços Digitais",
        "Lazer e Entretenimento",
        "Vestuário e Calçados",
        "Moradia",
        "Contas de Consumo",
        "Pets",
        "Viagens",
    ]

    for categoria in categorias_despesa:
        op.execute(
            f"INSERT INTO categorias_despesa (id, descricao) VALUES ('{uuid.uuid4()}', '{categoria}')"
        )


def downgrade() -> None:
    op.drop_table("categorias_despesa")
