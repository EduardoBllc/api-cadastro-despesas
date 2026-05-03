from __future__ import annotations

import uuid  # noqa: TC003
from datetime import datetime  # noqa: TC003
from decimal import Decimal  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.item import RespostaItem  # noqa: TC001


class CriarItemDespesa(BaseModel):
    item_id: uuid.UUID
    quantidade: Decimal = Field(gt=0, decimal_places=2, max_digits=9)
    valor_unitario: Decimal = Field(gt=0, decimal_places=2, max_digits=13)


class AtualizarItemDespesa(BaseModel):
    item_id: uuid.UUID | None = None
    quantidade: Decimal | None = Field(None, gt=0, decimal_places=2, max_digits=9)
    valor_unitario: Decimal | None = Field(None, gt=0, decimal_places=2, max_digits=13)


class RespostaItemDespesa(BaseModel):
    id: uuid.UUID
    despesa_id: uuid.UUID
    item_id: uuid.UUID | None
    item: RespostaItem | None
    quantidade: Decimal
    valor_unitario: Decimal
    valor_total: Decimal
    data_cadastro: datetime
    data_alteracao: datetime
    model_config = ConfigDict(from_attributes=True)
