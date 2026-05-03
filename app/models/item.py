from __future__ import annotations

import uuid  # noqa: TC003
from decimal import Decimal  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.categoria_item import CategoriaItem
    from app.models.historico_preco_item import HistoricoPrecoItem
    from app.models.item_despesa import ItemDespesa
    from app.models.unidade_medida import UnidadeMedida


class Item(BaseModel):
    __tablename__ = "itens"

    descricao: Mapped[str] = mapped_column(String(120))
    categoria_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categorias_item.id", ondelete="RESTRICT")
    )
    unidade_medida_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("unidades_medida.id", ondelete="SET NULL")
    )
    valor_referencia: Mapped[Decimal | None] = mapped_column(Numeric(13, 2))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    categoria_item: Mapped[CategoriaItem] = relationship(back_populates="itens")
    unidade_medida: Mapped[UnidadeMedida | None] = relationship(back_populates="itens")
    itens_despesa: Mapped[list[ItemDespesa]] = relationship(back_populates="item")
    historico_precos: Mapped[list[HistoricoPrecoItem]] = relationship(back_populates="item")
