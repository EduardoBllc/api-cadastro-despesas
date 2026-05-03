from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.despesa import Despesa


class CategoriaDespesa(BaseModel):
    __tablename__ = "categorias_despesa"

    descricao: Mapped[str] = mapped_column(String(60))

    despesas: Mapped[list[Despesa]] = relationship(back_populates="categoria_despesa")
