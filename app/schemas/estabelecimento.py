from __future__ import annotations

import uuid  # noqa: TC003
from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.tipo_estabelecimento import RespostaTipoEstabelecimento  # noqa: TC001


class CriarEstabelecimento(BaseModel):
    descricao: str = Field(max_length=100)
    tipo_id: uuid.UUID


class AtualizarEstabelecimento(BaseModel):
    descricao: str | None = Field(None, max_length=100)
    tipo_id: uuid.UUID | None = None


class RespostaEstabelecimento(BaseModel):
    id: uuid.UUID
    descricao: str
    tipo_id: uuid.UUID
    tipo: RespostaTipoEstabelecimento
    data_cadastro: datetime
    data_alteracao: datetime
    model_config = ConfigDict(from_attributes=True)
