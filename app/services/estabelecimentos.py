from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models import Estabelecimento

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas import AtualizarEstabelecimento, CriarEstabelecimento

_OPTS = [selectinload(Estabelecimento.tipo)]


async def listar(session: AsyncSession) -> list[Estabelecimento]:
    result = await session.execute(
        select(Estabelecimento).options(*_OPTS).order_by(Estabelecimento.descricao)
    )
    return list(result.scalars().all())


async def criar(session: AsyncSession, body: CriarEstabelecimento) -> Estabelecimento:
    estabelecimento = Estabelecimento(**body.model_dump())
    session.add(estabelecimento)
    await session.flush()
    result = await session.execute(
        select(Estabelecimento).where(Estabelecimento.id == estabelecimento.id).options(*_OPTS)
    )
    return result.scalar_one()


async def obter(session: AsyncSession, estabelecimento_id: uuid.UUID) -> Estabelecimento:
    result = await session.execute(
        select(Estabelecimento).where(Estabelecimento.id == estabelecimento_id).options(*_OPTS)
    )
    estabelecimento = result.scalar_one_or_none()
    if estabelecimento is None:
        raise HTTPException(status_code=404, detail="Estabelecimento não encontrado")
    return estabelecimento


async def atualizar(
    session: AsyncSession, estabelecimento_id: uuid.UUID, body: AtualizarEstabelecimento
) -> Estabelecimento:
    result = await session.execute(
        select(Estabelecimento).where(Estabelecimento.id == estabelecimento_id).options(*_OPTS)
    )
    estabelecimento = result.scalar_one_or_none()
    if estabelecimento is None:
        raise HTTPException(status_code=404, detail="Estabelecimento não encontrado")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(estabelecimento, field, value)

    await session.flush()
    result = await session.execute(
        select(Estabelecimento)
        .where(Estabelecimento.id == estabelecimento_id)
        .options(*_OPTS)
        .execution_options(populate_existing=True)
    )
    return result.scalar_one()


async def excluir(session: AsyncSession, estabelecimento_id: uuid.UUID) -> None:
    estabelecimento = await session.get(Estabelecimento, estabelecimento_id)
    if estabelecimento is None:
        raise HTTPException(status_code=404, detail="Estabelecimento não encontrado")
    try:
        await session.delete(estabelecimento)
        await session.flush()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409, detail="Estabelecimento em uso por uma ou mais despesas"
        ) from exc
