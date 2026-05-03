from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import UnidadeMedida

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas import AtualizarUnidadeMedida, CriarUnidadeMedida


async def listar(session: AsyncSession) -> list[UnidadeMedida]:
    result = await session.execute(select(UnidadeMedida).order_by(UnidadeMedida.descricao))
    return list(result.scalars().all())


async def criar(session: AsyncSession, body: CriarUnidadeMedida) -> UnidadeMedida:
    unidade = UnidadeMedida(**body.model_dump())
    session.add(unidade)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Unidade de medida já cadastrada") from exc
    await session.refresh(unidade)
    return unidade


async def obter(session: AsyncSession, unidade_id: uuid.UUID) -> UnidadeMedida:
    unidade = await session.get(UnidadeMedida, unidade_id)
    if unidade is None:
        raise HTTPException(status_code=404, detail="Unidade de medida não encontrada")
    return unidade


async def atualizar(
    session: AsyncSession, unidade_id: uuid.UUID, body: AtualizarUnidadeMedida
) -> UnidadeMedida:
    unidade = await session.get(UnidadeMedida, unidade_id)
    if unidade is None:
        raise HTTPException(status_code=404, detail="Unidade de medida não encontrada")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(unidade, field, value)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Unidade de medida já cadastrada") from exc
    await session.refresh(unidade)
    return unidade


async def excluir(session: AsyncSession, unidade_id: uuid.UUID) -> None:
    unidade = await session.get(UnidadeMedida, unidade_id)
    if unidade is None:
        raise HTTPException(status_code=404, detail="Unidade de medida não encontrada")
    try:
        await session.delete(unidade)
        await session.flush()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409, detail="Unidade de medida em uso por um ou mais itens"
        ) from exc
