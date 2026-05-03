from __future__ import annotations

import uuid  # noqa: TC003
from datetime import date  # noqa: TC003
from decimal import Decimal  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.carro import Carro
    from app.models.despesa import Despesa
    from app.models.estabelecimento import Estabelecimento


class Abastecimento(BaseModel):
    __tablename__ = "abastecimentos"

    despesa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("despesas.id", ondelete="CASCADE"), unique=True
    )
    carro_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("carros.id", ondelete="RESTRICT"))
    posto_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("estabelecimentos.id", ondelete="SET NULL")
    )
    data_abastecimento: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    quilometragem: Mapped[int] = mapped_column(Integer)
    litros: Mapped[Decimal] = mapped_column(Numeric(9, 3))
    observacao: Mapped[str | None] = mapped_column(Text)

    despesa: Mapped[Despesa] = relationship(back_populates="abastecimento")
    carro: Mapped[Carro] = relationship(back_populates="abastecimentos")
    posto: Mapped[Estabelecimento | None] = relationship()
