from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas import AtualizarConfiguracao, RespostaConfiguracao
from app.services import configuracoes as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import Configuracao

router = APIRouter(prefix="/configuracoes", tags=["configuracoes"])


@router.get("", response_model=list[RespostaConfiguracao])
async def listar_configuracoes(
    session: AsyncSession = Depends(get_db),
) -> list[Configuracao]:
    return await service.listar(session)


@router.put("/{chave}", response_model=RespostaConfiguracao)
async def atualizar_configuracao(
    chave: str, body: AtualizarConfiguracao, session: AsyncSession = Depends(get_db)
) -> Configuracao:
    return await service.atualizar(session, chave, body)
