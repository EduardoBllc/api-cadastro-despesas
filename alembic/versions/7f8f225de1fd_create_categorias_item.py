"""create_categorias_item

Revision ID: 7f8f225de1fd
Revises: 3910ca32739c
Create Date: 2026-04-28 10:05:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
import uuid

# revision identifiers, used by Alembic.
revision: str = "7f8f225de1fd"
down_revision: Union[str, None] = "3910ca32739c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categorias_item",
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

    categorias_itens = [
        "Laticínios e Ovos",
        "Carnes, Aves e Peixes",
        "Hortifruti",
        "Mercearia",
        "Bebidas",
        "Frios e Embutidos",
        "Padaria e Confeitaria",
        "Snacks e Guloseimas",
        "Higiene Pessoal",
        "Cosméticos e Beleza",
        "Limpeza e Organização",
        "Medicamentos",
        "Vitaminas e Suplementos",
        "Material Escolar e Escritório",
        "Roupas e Calçados",
        "Eletrônicos e Informática",
        "Serviços",
    ]

    for categoria in categorias_itens:
        op.execute(
            f"INSERT INTO categorias_item (id, descricao) VALUES ('{uuid.uuid4()}', '{categoria}')"
        )


def downgrade() -> None:
    op.drop_table("categorias_item")
