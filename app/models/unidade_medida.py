from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.item import Item


class UnidadeMedida(BaseModel):
    __tablename__ = "unidades_medida"

    descricao: Mapped[str] = mapped_column(String(60), unique=True)

    itens: Mapped[list[Item]] = relationship(back_populates="unidade_medida")
