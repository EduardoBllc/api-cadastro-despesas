from __future__ import annotations

import uuid  # noqa: TC003
from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field


class CriarCarro(BaseModel):
    nome: str = Field(max_length=60)
    placa: str | None = Field(None, max_length=8)


class AtualizarCarro(BaseModel):
    nome: str | None = Field(None, max_length=60)
    placa: str | None = Field(None, max_length=8)
    ativo: bool | None = None


class RespostaCarro(BaseModel):
    id: uuid.UUID
    nome: str
    placa: str | None
    ativo: bool
    data_cadastro: datetime
    data_alteracao: datetime
    model_config = ConfigDict(from_attributes=True)
