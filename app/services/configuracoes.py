from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select

from app.models import Configuracao

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas import AtualizarConfiguracao


async def listar(session: AsyncSession) -> list[Configuracao]:
    result = await session.execute(select(Configuracao).order_by(Configuracao.chave))
    return list(result.scalars().all())


async def atualizar(
    session: AsyncSession, chave: str, body: AtualizarConfiguracao
) -> Configuracao:
    result = await session.execute(select(Configuracao).where(Configuracao.chave == chave))
    conf = result.scalar_one_or_none()
    if conf is None:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    conf.valor = body.valor
    await session.flush()
    await session.refresh(conf)
    return conf
