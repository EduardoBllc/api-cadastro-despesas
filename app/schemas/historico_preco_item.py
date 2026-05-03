from __future__ import annotations

import uuid  # noqa: TC003
from datetime import date, datetime  # noqa: TC003
from decimal import Decimal  # noqa: TC003

from pydantic import BaseModel, ConfigDict


class RespostaHistoricoPrecoItem(BaseModel):
    id: uuid.UUID
    item_id: uuid.UUID
    item_despesa_id: uuid.UUID
    estabelecimento_id: uuid.UUID
    valor_unitario: Decimal
    data_despesa: date
    data_cadastro: datetime
    data_alteracao: datetime
    model_config = ConfigDict(from_attributes=True)
