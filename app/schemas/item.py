from __future__ import annotations

import uuid  # noqa: TC003
from datetime import datetime  # noqa: TC003
from decimal import Decimal  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.unidade_medida import RespostaUnidadeMedida


class CriarItem(BaseModel):
    descricao: str = Field(max_length=120)
    categoria_item_id: uuid.UUID
    unidade_medida_id: uuid.UUID | None = None
    valor_referencia: Decimal | None = Field(None, gt=0, decimal_places=2, max_digits=13)


class AtualizarItem(BaseModel):
    descricao: str | None = Field(None, max_length=120)
    categoria_item_id: uuid.UUID | None = None
    unidade_medida_id: uuid.UUID | None = None
    valor_referencia: Decimal | None = Field(None, gt=0, decimal_places=2, max_digits=13)
    ativo: bool | None = None


class RespostaItem(BaseModel):
    id: uuid.UUID
    descricao: str
    categoria_item_id: uuid.UUID
    unidade_medida_id: uuid.UUID | None
    unidade_medida: RespostaUnidadeMedida | None
    valor_referencia: Decimal | None
    ativo: bool
    data_cadastro: datetime
    data_alteracao: datetime
    model_config = ConfigDict(from_attributes=True)
