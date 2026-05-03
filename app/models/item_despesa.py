from __future__ import annotations

import uuid  # noqa: TC003
from decimal import Decimal  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import Computed, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.despesa import Despesa
    from app.models.historico_preco_item import HistoricoPrecoItem
    from app.models.item import Item


class ItemDespesa(BaseModel):
    __tablename__ = "itens_despesa"

    despesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("despesas.id", ondelete="CASCADE"))
    item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("itens.id", ondelete="RESTRICT"))
    quantidade: Mapped[Decimal] = mapped_column(Numeric(10, 3))
    valor_unitario: Mapped[Decimal] = mapped_column(Numeric(13, 2))
    valor_total: Mapped[Decimal] = mapped_column(
        Numeric(13, 2), Computed("quantidade * valor_unitario", persisted=True)
    )

    despesa: Mapped[Despesa] = relationship(back_populates="itens")
    item: Mapped[Item | None] = relationship(back_populates="itens_despesa")
    historico: Mapped[HistoricoPrecoItem | None] = relationship(
        back_populates="item_despesa", uselist=False, cascade="all, delete-orphan"
    )
