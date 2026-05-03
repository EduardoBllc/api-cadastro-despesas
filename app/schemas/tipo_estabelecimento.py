from __future__ import annotations

import uuid  # noqa: TC003
from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field


class CriarTipoEstabelecimento(BaseModel):
    descricao: str = Field(max_length=60)


class AtualizarTipoEstabelecimento(BaseModel):
    descricao: str = Field(max_length=60)


class RespostaTipoEstabelecimento(BaseModel):
    id: uuid.UUID
    descricao: str
    data_cadastro: datetime
    data_alteracao: datetime
    model_config = ConfigDict(from_attributes=True)
