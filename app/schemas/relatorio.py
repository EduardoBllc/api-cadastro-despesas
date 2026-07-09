from __future__ import annotations

import uuid  # noqa: TC003
from datetime import date  # noqa: TC003
from decimal import Decimal  # noqa: TC003

from pydantic import BaseModel


class GastoMensal(BaseModel):
    mes: int
    total: Decimal
    quantidade: int
    ticket_medio: Decimal | None = None


class GastoCategoria(BaseModel):
    categoria_id: uuid.UUID
    categoria_descricao: str
    total: Decimal
    quantidade: int
    percentual: Decimal


class AbastecimentoMensal(BaseModel):
    mes: int
    total_gasto: Decimal
    total_litros: Decimal
    quantidade: int


class AbastecimentoEficiencia(BaseModel):
    data_abastecimento: date
    quilometragem: int
    km_rodados: int | None
    km_por_litro: Decimal | None
    valor_por_litro: Decimal
    total_gasto: Decimal
