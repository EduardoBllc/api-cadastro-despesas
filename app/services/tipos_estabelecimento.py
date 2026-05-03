from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import TipoEstabelecimento

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas import AtualizarTipoEstabelecimento, CriarTipoEstabelecimento


async def listar(session: AsyncSession) -> list[TipoEstabelecimento]:
    result = await session.execute(select(TipoEstabelecimento).order_by(TipoEstabelecimento.descricao))
    return list(result.scalars().all())


async def criar(session: AsyncSession, body: CriarTipoEstabelecimento) -> TipoEstabelecimento:
    tipo = TipoEstabelecimento(**body.model_dump())
    session.add(tipo)
    await session.flush()
    await session.refresh(tipo)
    return tipo


async def obter(session: AsyncSession, tipo_id: uuid.UUID) -> TipoEstabelecimento:
    tipo = await session.get(TipoEstabelecimento, tipo_id)
    if tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de estabelecimento não encontrado")
    return tipo


async def atualizar(
    session: AsyncSession, tipo_id: uuid.UUID, body: AtualizarTipoEstabelecimento
) -> TipoEstabelecimento:
    tipo = await session.get(TipoEstabelecimento, tipo_id)
    if tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de estabelecimento não encontrado")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(tipo, field, value)
    await session.flush()
    await session.refresh(tipo)
    return tipo


async def excluir(session: AsyncSession, tipo_id: uuid.UUID) -> None:
    tipo = await session.get(TipoEstabelecimento, tipo_id)
    if tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de estabelecimento não encontrado")
    try:
        await session.delete(tipo)
        await session.flush()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409, detail="Tipo em uso por um ou mais estabelecimentos"
        ) from exc
