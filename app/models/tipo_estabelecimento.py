from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class TipoEstabelecimento(BaseModel):
    __tablename__ = "tipos_estabelecimento"

    descricao: Mapped[str] = mapped_column(String(60), unique=True)
