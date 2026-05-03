from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Query

from app.database import get_db
from app.schemas import RespostaPaginadaAbastecimento
from app.services import abastecimentos as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/abastecimentos", tags=["abastecimentos"])


@router.get("", response_model=RespostaPaginadaAbastecimento)
async def listar_abastecimentos(
    session: AsyncSession = Depends(get_db),
    carro_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> RespostaPaginadaAbastecimento:
    return await service.listar(session, carro_id, page, page_size)
