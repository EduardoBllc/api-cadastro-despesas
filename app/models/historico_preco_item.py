from __future__ import annotations

import uuid  # noqa: TC003
from datetime import date  # noqa: TC003
from decimal import Decimal  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.estabelecimento import Estabelecimento
    from app.models.item import Item
    from app.models.item_despesa import ItemDespesa


class HistoricoPrecoItem(BaseModel):
    __tablename__ = "historico_preco_itens"

    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("itens.id", ondelete="CASCADE"))
    item_despesa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("itens_despesa.id", ondelete="CASCADE"), unique=True
    )
    estabelecimento_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("estabelecimentos.id", ondelete="RESTRICT")
    )
    valor_unitario: Mapped[Decimal] = mapped_column(Numeric(13, 2))
    data_despesa: Mapped[date] = mapped_column(Date)

    item: Mapped[Item] = relationship(back_populates="historico_precos")
    item_despesa: Mapped[ItemDespesa] = relationship(back_populates="historico")
    estabelecimento: Mapped[Estabelecimento] = relationship()
