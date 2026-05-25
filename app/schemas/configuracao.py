from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

_TIPO_MAP: dict[str, type] = {
    "int": int,
    "float": float,
    "bool": bool,
    "str": str,
}


class AtualizarConfiguracao(BaseModel):
    valor: Any


class RespostaConfiguracao(BaseModel):
    chave: str
    tipo: str
    valor: Any
    data_cadastro: datetime
    data_alteracao: datetime
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def _parse_valor(self) -> RespostaConfiguracao:
        if self.valor is not None and self.tipo in _TIPO_MAP:
            self.valor = _TIPO_MAP[self.tipo](self.valor)
        return self
