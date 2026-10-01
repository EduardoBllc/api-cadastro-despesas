"""Add importação NFC-e (cnpj, chave_nfce, vinculos_produto_nfce)

Revision ID: 5c2e9a1f7b3d
Revises: 73d7225ddc86
Create Date: 2026-09-30 10:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5c2e9a1f7b3d"
down_revision: str | Sequence[str] | None = "73d7225ddc86"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("estabelecimentos", sa.Column("cnpj", sa.String(length=14), nullable=True))
    op.create_unique_constraint("estabelecimentos_cnpj_key", "estabelecimentos", ["cnpj"])
    op.add_column("despesas", sa.Column("chave_nfce", sa.CHAR(length=44), nullable=True))
    op.create_unique_constraint("despesas_chave_nfce_key", "despesas", ["chave_nfce"])
    op.create_table(
        "vinculos_produto_nfce",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cnpj_raiz", sa.String(length=8), nullable=False),
        sa.Column("codigo_produto", sa.String(length=60), nullable=False),
        sa.Column("item_id", sa.Uuid(), nullable=False),
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
        sa.ForeignKeyConstraint(["item_id"], ["itens.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cnpj_raiz", "codigo_produto"),
    )


def downgrade() -> None:
    op.drop_table("vinculos_produto_nfce")
    op.drop_constraint("despesas_chave_nfce_key", "despesas", type_="unique")
    op.drop_column("despesas", "chave_nfce")
    op.drop_constraint("estabelecimentos_cnpj_key", "estabelecimentos", type_="unique")
    op.drop_column("estabelecimentos", "cnpj")
