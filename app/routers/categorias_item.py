from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas import AtualizarCategoriaItem, CriarCategoriaItem, RespostaCategoriaItem
from app.services import categorias_item as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import CategoriaItem

router = APIRouter(prefix="/categorias-item", tags=["categorias-item"])


@router.get("", response_model=list[RespostaCategoriaItem])
async def listar_categorias_item(
    session: AsyncSession = Depends(get_db),
) -> list[CategoriaItem]:
    return await service.listar(session)


@router.post("", response_model=RespostaCategoriaItem, status_code=201)
async def criar_categoria_item(
    body: CriarCategoriaItem, session: AsyncSession = Depends(get_db)
) -> CategoriaItem:
    return await service.criar(session, body)


@router.get("/{categoria_id}", response_model=RespostaCategoriaItem)
async def obter_categoria_item(
    categoria_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> CategoriaItem:
    return await service.obter(session, categoria_id)


@router.put("/{categoria_id}", response_model=RespostaCategoriaItem)
async def atualizar_categoria_item(
    categoria_id: uuid.UUID,
    body: AtualizarCategoriaItem,
    session: AsyncSession = Depends(get_db),
) -> CategoriaItem:
    return await service.atualizar(session, categoria_id, body)


@router.delete("/{categoria_id}", status_code=204)
async def excluir_categoria_item(
    categoria_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> None:
    await service.excluir(session, categoria_id)
