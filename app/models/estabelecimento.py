from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.despesa import Despesa
    from app.models.tipo_estabelecimento import TipoEstabelecimento


class Estabelecimento(BaseModel):
    __tablename__ = "estabelecimentos"

    descricao: Mapped[str] = mapped_column(String(100))
    tipo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tipos_estabelecimento.id", ondelete="RESTRICT")
    )

    tipo: Mapped[TipoEstabelecimento] = relationship()
    despesas: Mapped[list[Despesa]] = relationship(back_populates="estabelecimento")
