from __future__ import annotations

import uuid  # noqa: TC003
from datetime import date, datetime
from decimal import Decimal  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.abastecimento import CriarAbastecimento, RespostaAbastecimento  # noqa: TC001
from app.schemas.estabelecimento import RespostaEstabelecimento  # noqa: TC001
from app.schemas.item_despesa import (  # noqa: TC001
    CriarItemDespesa,
    ItemDespesaParaAtualizar,
    RespostaItemDespesa,
)


class CriarDespesa(BaseModel):
    data_despesa: date = Field(default_factory=date.today)
    estabelecimento_id: uuid.UUID
    categoria_despesa_id: uuid.UUID
    valor_total: Decimal = Field(gt=0, decimal_places=2, max_digits=13)
    observacao: str | None = None
    itens: list[CriarItemDespesa] = Field(default_factory=list)
    abastecimento: CriarAbastecimento | None = None


class AtualizarDespesa(BaseModel):
    data_despesa: date | None = None
    estabelecimento_id: uuid.UUID | None = None
    categoria_despesa_id: uuid.UUID | None = None
    valor_total: Decimal | None = Field(None, gt=0, decimal_places=2, max_digits=13)
    observacao: str | None = None
    itens: list[ItemDespesaParaAtualizar] | None = None


class RespostaDespesaLista(BaseModel):
    id: uuid.UUID
    data_despesa: date
    estabelecimento_id: uuid.UUID
    estabelecimento: RespostaEstabelecimento
    categoria_despesa_id: uuid.UUID
    valor_total: Decimal
    observacao: str | None
    data_cadastro: datetime
    data_alteracao: datetime
    model_config = ConfigDict(from_attributes=True)


class RespostaDespesaDetalhe(RespostaDespesaLista):
    itens: list[RespostaItemDespesa]
    abastecimento: RespostaAbastecimento | None = None


class RespostaPaginadaDespesa(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[RespostaDespesaLista]
