from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import Carro

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas import AtualizarCarro, CriarCarro


async def listar(session: AsyncSession) -> list[Carro]:
    result = await session.execute(select(Carro).order_by(Carro.nome))
    return list(result.scalars().all())


async def criar(session: AsyncSession, body: CriarCarro) -> Carro:
    carro = Carro(**body.model_dump())
    session.add(carro)
    await session.flush()
    await session.refresh(carro)
    return carro


async def obter(session: AsyncSession, carro_id: uuid.UUID) -> Carro:
    carro = await session.get(Carro, carro_id)
    if carro is None:
        raise HTTPException(status_code=404, detail="Carro não encontrado")
    return carro


async def atualizar(session: AsyncSession, carro_id: uuid.UUID, body: AtualizarCarro) -> Carro:
    carro = await session.get(Carro, carro_id)
    if carro is None:
        raise HTTPException(status_code=404, detail="Carro não encontrado")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(carro, field, value)
    await session.flush()
    await session.refresh(carro)
    return carro


async def excluir(session: AsyncSession, carro_id: uuid.UUID) -> None:
    carro = await session.get(Carro, carro_id)
    if carro is None:
        raise HTTPException(status_code=404, detail="Carro não encontrado")
    try:
        await session.delete(carro)
        await session.flush()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409, detail="Carro em uso por um ou mais abastecimentos"
        ) from exc
