from __future__ import annotations

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Configuracao(BaseModel):
    __tablename__ = "configuracoes"
    __table_args__ = (UniqueConstraint("chave"),)

    chave: Mapped[str] = mapped_column(String(60))
    tipo: Mapped[str] = mapped_column(String(20))
    valor: Mapped[str | None] = mapped_column(Text)
