from __future__ import annotations

import uuid  # noqa: TC003
from datetime import date  # noqa: TC003
from decimal import Decimal  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.abastecimento import Abastecimento
    from app.models.categoria_despesa import CategoriaDespesa
    from app.models.estabelecimento import Estabelecimento
    from app.models.item_despesa import ItemDespesa


class Despesa(BaseModel):
    __tablename__ = "despesas"

    data_despesa: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    estabelecimento_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("estabelecimentos.id", ondelete="RESTRICT")
    )
    categoria_despesa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categorias_despesa.id", ondelete="RESTRICT")
    )
    valor_total: Mapped[Decimal] = mapped_column(Numeric(13, 2))
    observacao: Mapped[str | None] = mapped_column(Text)

    estabelecimento: Mapped[Estabelecimento] = relationship(back_populates="despesas")
    categoria_despesa: Mapped[CategoriaDespesa] = relationship(back_populates="despesas")
    itens: Mapped[list[ItemDespesa]] = relationship(
        back_populates="despesa", cascade="all, delete-orphan"
    )
    abastecimento: Mapped[Abastecimento | None] = relationship(
        back_populates="despesa", uselist=False, cascade="all, delete-orphan"
    )
