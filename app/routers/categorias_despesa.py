from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas import AtualizarCategoriaDespesa, CriarCategoriaDespesa, RespostaCategoriaDespesa
from app.services import categorias_despesa as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import CategoriaDespesa

router = APIRouter(prefix="/categorias-despesa", tags=["categorias-despesa"])


@router.get("", response_model=list[RespostaCategoriaDespesa])
async def listar_categorias_despesa(
    session: AsyncSession = Depends(get_db),
) -> list[CategoriaDespesa]:
    return await service.listar(session)


@router.post("", response_model=RespostaCategoriaDespesa, status_code=201)
async def criar_categoria_despesa(
    body: CriarCategoriaDespesa, session: AsyncSession = Depends(get_db)
) -> CategoriaDespesa:
    return await service.criar(session, body)


@router.get("/{categoria_id}", response_model=RespostaCategoriaDespesa)
async def obter_categoria_despesa(
    categoria_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> CategoriaDespesa:
    return await service.obter(session, categoria_id)


@router.put("/{categoria_id}", response_model=RespostaCategoriaDespesa)
async def atualizar_categoria_despesa(
    categoria_id: uuid.UUID,
    body: AtualizarCategoriaDespesa,
    session: AsyncSession = Depends(get_db),
) -> CategoriaDespesa:
    return await service.atualizar(session, categoria_id, body)


@router.delete("/{categoria_id}", status_code=204)
async def excluir_categoria_despesa(
    categoria_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> None:
    await service.excluir(session, categoria_id)
