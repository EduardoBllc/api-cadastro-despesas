from __future__ import annotations

import uuid
from pydantic import BaseModel, ConfigDict


class SugestaoCategoria(BaseModel):
    id: uuid.UUID
    descricao: str
    confianca: float # Frequência relativa do uso dessa categoria para o termo
    model_config = ConfigDict(from_attributes=True)


class RespostaSugestoes(BaseModel):
    sugestoes: list[SugestaoCategoria]
