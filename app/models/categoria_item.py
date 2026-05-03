from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.item import Item


class CategoriaItem(BaseModel):
    __tablename__ = "categorias_item"

    descricao: Mapped[str] = mapped_column(String(60))

    itens: Mapped[list[Item]] = relationship(back_populates="categoria_item")
