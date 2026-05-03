from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Despesa, HistoricoPrecoItem, Item, ItemDespesa

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas import AtualizarItemDespesa, CriarItemDespesa


async def _get_despesa_or_404(session: AsyncSession, despesa_id: uuid.UUID) -> Despesa:
    despesa = await session.get(Despesa, despesa_id)
    if despesa is None:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return despesa


async def _registrar_historico(
    session: AsyncSession, item_despesa: ItemDespesa, despesa: Despesa
) -> None:
    result = await session.execute(
        select(HistoricoPrecoItem).where(
            HistoricoPrecoItem.item_despesa_id == item_despesa.id
        )
    )
    historico = result.scalar_one_or_none()

    if historico is None:
        historico = HistoricoPrecoItem(
            item_id=item_despesa.item_id,
            item_despesa_id=item_despesa.id,
            estabelecimento_id=despesa.estabelecimento_id,
            valor_unitario=item_despesa.valor_unitario,
            data_despesa=despesa.data_despesa,
        )
        session.add(historico)
    else:
        historico.item_id = item_despesa.item_id
        historico.valor_unitario = item_despesa.valor_unitario
        historico.data_despesa = despesa.data_despesa
        historico.estabelecimento_id = despesa.estabelecimento_id

    if item_despesa.item_id is not None:
        item_obj = await session.get(Item, item_despesa.item_id)
        if item_obj is not None:
            item_obj.valor_referencia = item_despesa.valor_unitario


async def listar(session: AsyncSession, despesa_id: uuid.UUID) -> list[ItemDespesa]:
    await _get_despesa_or_404(session, despesa_id)
    result = await session.execute(
        select(ItemDespesa)
        .where(ItemDespesa.despesa_id == despesa_id)
        .options(selectinload(ItemDespesa.item))
    )
    return list(result.scalars().all())


async def criar(
    session: AsyncSession, despesa_id: uuid.UUID, body: CriarItemDespesa
) -> ItemDespesa:
    despesa = await _get_despesa_or_404(session, despesa_id)
    item_despesa = ItemDespesa(despesa_id=despesa_id, **body.model_dump())
    session.add(item_despesa)
    await session.flush()
    await _registrar_historico(session, item_despesa, despesa)
    await session.refresh(item_despesa)
    return item_despesa


async def obter(
    session: AsyncSession, despesa_id: uuid.UUID, item_id: uuid.UUID
) -> ItemDespesa:
    await _get_despesa_or_404(session, despesa_id)
    result = await session.execute(
        select(ItemDespesa)
        .where(ItemDespesa.id == item_id, ItemDespesa.despesa_id == despesa_id)
        .options(selectinload(ItemDespesa.item))
    )
    item_despesa = result.scalar_one_or_none()
    if item_despesa is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item_despesa


async def atualizar(
    session: AsyncSession,
    despesa_id: uuid.UUID,
    item_id: uuid.UUID,
    body: AtualizarItemDespesa,
) -> ItemDespesa:
    despesa = await _get_despesa_or_404(session, despesa_id)
    result = await session.execute(
        select(ItemDespesa).where(ItemDespesa.id == item_id, ItemDespesa.despesa_id == despesa_id)
    )
    item_despesa = result.scalar_one_or_none()
    if item_despesa is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item_despesa, field, value)
    await session.flush()
    await _registrar_historico(session, item_despesa, despesa)
    await session.refresh(item_despesa)
    return item_despesa


async def excluir(session: AsyncSession, despesa_id: uuid.UUID, item_id: uuid.UUID) -> None:
    await _get_despesa_or_404(session, despesa_id)
    result = await session.execute(
        select(ItemDespesa).where(ItemDespesa.id == item_id, ItemDespesa.despesa_id == despesa_id)
    )
    item_despesa = result.scalar_one_or_none()
    if item_despesa is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    await session.delete(item_despesa)
