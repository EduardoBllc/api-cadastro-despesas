from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models import Item

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas import AtualizarItem, CriarItem

_OPTS = [selectinload(Item.unidade_medida)]


async def _get(session: AsyncSession, item_id: uuid.UUID) -> Item:
    stmt = select(Item).options(*_OPTS).where(Item.id == item_id)
    item = (await session.execute(stmt)).scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item


async def listar(session: AsyncSession, ativo: bool | None = None) -> list[Item]:
    stmt = select(Item).options(*_OPTS).order_by(Item.descricao)
    if ativo is not None:
        stmt = stmt.where(Item.ativo == ativo)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def criar(session: AsyncSession, body: CriarItem) -> Item:
    item = Item(**body.model_dump())
    session.add(item)
    await session.flush()
    return await _get(session, item.id)


async def obter(session: AsyncSession, item_id: uuid.UUID) -> Item:
    return await _get(session, item_id)


async def atualizar(session: AsyncSession, item_id: uuid.UUID, body: AtualizarItem) -> Item:
    item = await session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await session.flush()
    return await _get(session, item.id)


async def excluir(session: AsyncSession, item_id: uuid.UUID) -> None:
    item = await session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    try:
        await session.delete(item)
        await session.flush()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409, detail="Item em uso por uma ou mais despesas"
        ) from exc
