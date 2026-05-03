from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas import AtualizarItemDespesa, CriarItemDespesa, RespostaItemDespesa
from app.services import itens_despesa as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import ItemDespesa

router = APIRouter(prefix="/despesas/{despesa_id}/itens", tags=["itens"])


@router.get("", response_model=list[RespostaItemDespesa])
async def listar_itens(
    despesa_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> list[ItemDespesa]:
    return await service.listar(session, despesa_id)


@router.post("", response_model=RespostaItemDespesa, status_code=201)
async def criar_item(
    despesa_id: uuid.UUID, body: CriarItemDespesa, session: AsyncSession = Depends(get_db)
) -> ItemDespesa:
    return await service.criar(session, despesa_id, body)


@router.get("/{item_id}", response_model=RespostaItemDespesa)
async def obter_item(
    despesa_id: uuid.UUID, item_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> ItemDespesa:
    return await service.obter(session, despesa_id, item_id)


@router.put("/{item_id}", response_model=RespostaItemDespesa)
async def atualizar_item(
    despesa_id: uuid.UUID,
    item_id: uuid.UUID,
    body: AtualizarItemDespesa,
    session: AsyncSession = Depends(get_db),
) -> ItemDespesa:
    return await service.atualizar(session, despesa_id, item_id, body)


@router.delete("/{item_id}", status_code=204)
async def excluir_item(
    despesa_id: uuid.UUID, item_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> None:
    await service.excluir(session, despesa_id, item_id)
