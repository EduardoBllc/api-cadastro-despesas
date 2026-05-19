"""create_configs_abastecimento

Revision ID: 0d58374ff365
Revises: c9d8e7f6a5b4
Create Date: 2026-05-15 23:05:13.190939

"""

from __future__ import annotations

import uuid
from collections.abc import Sequence  # noqa: TC003

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0d58374ff365"
down_revision: str | Sequence[str] | None = "c9d8e7f6a5b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    configuracoes_abastecimento = [
        {
            "chave": "categoria_abastecimento_id",
            "tipo": "int",
        },
        {
            "chave": "tipo_estabelecimento_posto_id",
            "tipo": "int",
        },
    ]

    for configuracao in configuracoes_abastecimento:
        op.execute(
            f"""
            INSERT INTO
                configuracoes (id, chave, tipo)
            VALUES
                ('{uuid.uuid4()}', '{configuracao["chave"]}', '{configuracao["tipo"]}')
            """
        )


def downgrade() -> None:
    """Downgrade schema."""
    pass
