from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Query

from app.database import get_db
from app.schemas import AtualizarItem, CriarItem, RespostaItem
from app.services import itens as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import Item

router = APIRouter(prefix="/itens", tags=["itens"])


@router.get("", response_model=list[RespostaItem])
async def listar_itens(
    ativo: Annotated[bool | None, Query()] = None,
    session: AsyncSession = Depends(get_db),
) -> list[Item]:
    return await service.listar(session, ativo=ativo)


@router.post("", response_model=RespostaItem, status_code=201)
async def criar_item(body: CriarItem, session: AsyncSession = Depends(get_db)) -> Item:
    return await service.criar(session, body)


@router.get("/{item_id}", response_model=RespostaItem)
async def obter_item(item_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> Item:
    return await service.obter(session, item_id)


@router.put("/{item_id}", response_model=RespostaItem)
async def atualizar_item(
    item_id: uuid.UUID, body: AtualizarItem, session: AsyncSession = Depends(get_db)
) -> Item:
    return await service.atualizar(session, item_id, body)


@router.delete("/{item_id}", status_code=204)
async def excluir_item(item_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> None:
    await service.excluir(session, item_id)
