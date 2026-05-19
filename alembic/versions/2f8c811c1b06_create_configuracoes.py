"""create_configuracoes

Revision ID: 2f8c811c1b06
Revises: 04d24be09647
Create Date: 2026-04-28 10:35:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2f8c811c1b06"
down_revision: str | Sequence[str] | None = "04d24be09647"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "configuracoes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("chave", sa.String(length=60), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("valor", sa.Text(), nullable=True),
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
        sa.UniqueConstraint("chave"),
    )


def downgrade() -> None:
    op.drop_table("configuracoes")
