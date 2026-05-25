"""create_config_unidade

Revision ID: 9972d28b97c3
Revises: 0d58374ff365
Create Date: 2026-05-18 23:25:07.864498

"""

from __future__ import annotations

import uuid
from collections.abc import Sequence  # noqa: TC003

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9972d28b97c3"
down_revision: str | Sequence[str] | None = "0d58374ff365"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CONFIGURACOES_UNITARIO = [
    {
        "chave": "medida_unitario_id",
        "tipo": "uuid",
    },
    {
        "chave": "valor_padrao_unitario",
        "tipo": "int",
    },
    {
        "chave": "autopreenche_unitario_quantidade",
        "tipo": "bool",
    },
    {
        "chave": "autopreenche_unitario_item",
        "tipo": "bool",
    },
]


def upgrade() -> None:
    for configuracao in CONFIGURACOES_UNITARIO:
        op.execute(
            f"""
            INSERT INTO
                configuracoes (id, chave, tipo)
            VALUES
                ('{uuid.uuid4()}', '{configuracao["chave"]}', '{configuracao["tipo"]}')
            """
        )


def downgrade() -> None:
    for configuracao in CONFIGURACOES_UNITARIO:
        op.execute(
            f"""
            DELETE FROM
                configuracoes
            WHERE
                chave = '{configuracao["chave"]}'
            """
        )
