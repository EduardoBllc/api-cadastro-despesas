from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import CategoriaDespesa

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas import AtualizarCategoriaDespesa, CriarCategoriaDespesa


async def listar(session: AsyncSession) -> list[CategoriaDespesa]:
    result = await session.execute(select(CategoriaDespesa).order_by(CategoriaDespesa.descricao))
    return list(result.scalars().all())


async def criar(session: AsyncSession, body: CriarCategoriaDespesa) -> CategoriaDespesa:
    categoria = CategoriaDespesa(**body.model_dump())
    session.add(categoria)
    await session.flush()
    await session.refresh(categoria)
    return categoria


async def obter(session: AsyncSession, categoria_id: uuid.UUID) -> CategoriaDespesa:
    categoria = await session.get(CategoriaDespesa, categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria


async def atualizar(
    session: AsyncSession, categoria_id: uuid.UUID, body: AtualizarCategoriaDespesa
) -> CategoriaDespesa:
    categoria = await session.get(CategoriaDespesa, categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(categoria, field, value)
    await session.flush()
    await session.refresh(categoria)
    return categoria


async def excluir(session: AsyncSession, categoria_id: uuid.UUID) -> None:
    categoria = await session.get(CategoriaDespesa, categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    try:
        await session.delete(categoria)
        await session.flush()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409, detail="Categoria em uso por uma ou mais despesas"
        ) from exc
