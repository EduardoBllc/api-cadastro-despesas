from __future__ import annotations

import uuid  # noqa: TC003
from datetime import date  # noqa: TC003
from decimal import Decimal  # noqa: TC003

from pydantic import BaseModel, Field

URL_MAX = 2000


class ImportarNfce(BaseModel):
    url: str = Field(min_length=1, max_length=URL_MAX)


class OrigemNfce(BaseModel):
    chave: str = Field(pattern=r"^\d{44}$")
    cnpj: str = Field(pattern=r"^\d{14}$")


class ItemRascunhoNfce(BaseModel):
    codigo: str
    descricao_nota: str
    unidade_nota: str
    quantidade: Decimal
    valor_unitario: Decimal
    valor_desconto: Decimal
    item_id: uuid.UUID | None


class RascunhoNfce(BaseModel):
    chave: str
    data_emissao: date
    cnpj: str
    razao_social: str
    endereco: str
    estabelecimento_id: uuid.UUID | None
    valor_pago: Decimal
    desconto_total: Decimal
    itens: list[ItemRascunhoNfce]
