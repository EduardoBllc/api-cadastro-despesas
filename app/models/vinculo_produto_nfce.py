from __future__ import annotations

import uuid  # noqa: TC003

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class VinculoProdutoNfce(BaseModel):
    __tablename__ = "vinculos_produto_nfce"
    __table_args__ = (UniqueConstraint("cnpj_raiz", "codigo_produto"),)

    cnpj_raiz: Mapped[str] = mapped_column(String(8))
    codigo_produto: Mapped[str] = mapped_column(String(60))
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("itens.id", ondelete="CASCADE"))
