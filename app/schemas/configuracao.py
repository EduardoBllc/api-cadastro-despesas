from __future__ import annotations

from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict


class AtualizarConfiguracao(BaseModel):
    valor: str | None


class RespostaConfiguracao(BaseModel):
    chave: str
    tipo: str
    valor: str | None
    data_cadastro: datetime
    data_alteracao: datetime
    model_config = ConfigDict(from_attributes=True)
