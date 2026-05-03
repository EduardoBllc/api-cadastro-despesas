from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models import Abastecimento, Carro, Despesa, Item, ItemDespesa, Estabelecimento
from app.services.itens_despesa import _registrar_historico
from app.schemas import (
    AtualizarAbastecimento,
    AtualizarDespesa,
    CriarAbastecimento,
    CriarDespesa,
    RespostaAbastecimento,
    RespostaDespesaDetalhe,
    RespostaPaginadaDespesa,
)
from app.services.abastecimentos import build_resposta as build_resposta_abastecimento

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

_OPTS = [
    selectinload(Despesa.itens).selectinload(ItemDespesa.item).selectinload(Item.unidade_medida),
    selectinload(Despesa.abastecimento),
    selectinload(Despesa.estabelecimento).selectinload(Estabelecimento.tipo),
]


async def _to_detalhe(session: AsyncSession, despesa: Despesa) -> RespostaDespesaDetalhe:
    resposta = RespostaDespesaDetalhe.model_validate(despesa)
    if despesa.abastecimento is not None:
        resposta.abastecimento = await build_resposta_abastecimento(
            session, despesa.abastecimento, despesa.valor_total
        )
    return resposta


async def get_or_404(session: AsyncSession, despesa_id: uuid.UUID) -> Despesa:
    result = await session.execute(select(Despesa).where(Despesa.id == despesa_id).options(*_OPTS))
    despesa = result.scalar_one_or_none()
    if despesa is None:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return despesa


async def listar(session: AsyncSession, page: int, page_size: int) -> RespostaPaginadaDespesa:
    offset = (page - 1) * page_size
    total = await session.scalar(select(func.count(Despesa.id)))
    result = await session.execute(
        select(Despesa)
        .options(selectinload(Despesa.estabelecimento).selectinload(Estabelecimento.tipo))
        .order_by(Despesa.data_despesa.desc())
        .offset(offset)
        .limit(page_size)
    )
    despesas = list(result.scalars().all())
    return RespostaPaginadaDespesa(total=total or 0, page=page, page_size=page_size, items=despesas)


async def criar(session: AsyncSession, body: CriarDespesa) -> RespostaDespesaDetalhe:
    if body.abastecimento is not None:
        carro = await session.get(Carro, body.abastecimento.carro_id)
        if carro is None:
            raise HTTPException(status_code=404, detail="Carro não encontrado")

    despesa = Despesa(**body.model_dump(exclude={"abastecimento", "itens"}))
    session.add(despesa)
    await session.flush()

    for item_data in body.itens:
        item_despesa = ItemDespesa(despesa_id=despesa.id, **item_data.model_dump())
        session.add(item_despesa)
        await session.flush()
        await _registrar_historico(session, item_despesa, despesa)

    if body.abastecimento is not None:
        ab_data = body.abastecimento.model_dump()
        ab_data["posto_id"] = despesa.estabelecimento_id
        session.add(Abastecimento(despesa_id=despesa.id, **ab_data))
        await session.flush()

    return await obter(session, despesa.id)


async def obter(session: AsyncSession, despesa_id: uuid.UUID) -> RespostaDespesaDetalhe:
    despesa = await get_or_404(session, despesa_id)
    return await _to_detalhe(session, despesa)


async def atualizar(
    session: AsyncSession, despesa_id: uuid.UUID, body: AtualizarDespesa
) -> RespostaDespesaDetalhe:
    despesa = await get_or_404(session, despesa_id)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(despesa, field, value)

    await session.flush()
    result = await session.execute(
        select(Despesa)
        .where(Despesa.id == despesa_id)
        .options(*_OPTS)
        .execution_options(populate_existing=True)
    )
    despesa = result.scalar_one()
    return await _to_detalhe(session, despesa)


async def excluir(session: AsyncSession, despesa_id: uuid.UUID) -> None:
    despesa = await session.get(Despesa, despesa_id)
    if despesa is None:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    await session.delete(despesa)


async def criar_abastecimento(
    session: AsyncSession, despesa_id: uuid.UUID, body: CriarAbastecimento
) -> RespostaAbastecimento:
    despesa = await get_or_404(session, despesa_id)

    if despesa.abastecimento is not None:
        raise HTTPException(status_code=409, detail="Despesa já possui abastecimento")

    carro = await session.get(Carro, body.carro_id)
    if carro is None:
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    ab = Abastecimento(despesa_id=despesa_id, **body.model_dump())
    session.add(ab)
    await session.flush()
    await session.refresh(ab)
    return await build_resposta_abastecimento(session, ab, despesa.valor_total)


async def atualizar_abastecimento(
    session: AsyncSession, despesa_id: uuid.UUID, body: AtualizarAbastecimento
) -> RespostaAbastecimento:
    despesa = await get_or_404(session, despesa_id)

    if despesa.abastecimento is None:
        raise HTTPException(status_code=404, detail="Despesa não possui abastecimento")

    if body.carro_id is not None:
        carro = await session.get(Carro, body.carro_id)
        if carro is None:
            raise HTTPException(status_code=404, detail="Carro não encontrado")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(despesa.abastecimento, field, value)

    await session.flush()
    await session.refresh(despesa.abastecimento)
    return await build_resposta_abastecimento(session, despesa.abastecimento, despesa.valor_total)


async def excluir_abastecimento(session: AsyncSession, despesa_id: uuid.UUID) -> None:
    despesa = await get_or_404(session, despesa_id)

    if despesa.abastecimento is None:
        raise HTTPException(status_code=404, detail="Despesa não possui abastecimento")

    await session.delete(despesa.abastecimento)
