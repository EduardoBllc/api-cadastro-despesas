from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.abastecimento import Abastecimento


class Carro(BaseModel):
    __tablename__ = "carros"

    nome: Mapped[str] = mapped_column(String(60))
    placa: Mapped[str | None] = mapped_column(String(8), unique=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))

    abastecimentos: Mapped[list[Abastecimento]] = relationship(back_populates="carro")
