from __future__ import annotations

import uuid  # noqa: TC003
from datetime import date, datetime
from decimal import Decimal  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field


class CriarAbastecimento(BaseModel):
    carro_id: uuid.UUID
    data_abastecimento: date = Field(default_factory=date.today)
    quilometragem: int = Field(gt=0)
    litros: Decimal = Field(gt=0, decimal_places=3, max_digits=9)
    observacao: str | None = None


class AtualizarAbastecimento(BaseModel):
    carro_id: uuid.UUID | None = None
    data_abastecimento: date | None = None
    quilometragem: int | None = Field(None, gt=0)
    litros: Decimal | None = Field(None, gt=0, decimal_places=3, max_digits=9)
    observacao: str | None = None


class RespostaAbastecimento(BaseModel):
    id: uuid.UUID
    despesa_id: uuid.UUID
    carro_id: uuid.UUID
    posto_id: uuid.UUID | None
    data_abastecimento: date
    quilometragem: int
    litros: Decimal
    valor_total: Decimal = Decimal("0")
    valor_por_litro: Decimal = Decimal("0")
    km_rodados: int | None = None
    km_por_litro: Decimal | None = None
    observacao: str | None
    data_cadastro: datetime
    data_alteracao: datetime
    model_config = ConfigDict(from_attributes=True)


class RespostaPaginadaAbastecimento(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[RespostaAbastecimento]
