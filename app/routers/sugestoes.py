from __future__ import annotations

from typing import TYPE_CHECKING
from fastapi import APIRouter, Depends, Query
from app.database import get_db
from app.schemas.sugestoes import RespostaSugestoes
from app.services import sugestoes as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/sugestoes", tags=["sugestoes"])


@router.get("/categoria-despesa", response_model=RespostaSugestoes)
async def sugerir_categoria_despesa(
    termo: str = Query(..., min_length=2),
    session: AsyncSession = Depends(get_db)
):
    """
    Sugere categorias de despesa com base no nome do estabelecimento.
    Analisa o histórico de despesas já cadastradas.
    """
    return await service.sugerir_categoria_despesa(session, termo)


@router.get("/categoria-item", response_model=RespostaSugestoes)
async def sugerir_categoria_item(
    termo: str = Query(..., min_length=2),
    session: AsyncSession = Depends(get_db)
):
    """
    Sugere categorias de item com base na descrição do item.
    Analisa o histórico de itens já cadastrados.
    """
    return await service.sugerir_categoria_item(session, termo)
