from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas import AtualizarEstabelecimento, CriarEstabelecimento, RespostaEstabelecimento
from app.services import estabelecimentos as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import Estabelecimento

router = APIRouter(prefix="/estabelecimentos", tags=["estabelecimentos"])


@router.get("", response_model=list[RespostaEstabelecimento])
async def listar_estabelecimentos(
    session: AsyncSession = Depends(get_db),
) -> list[Estabelecimento]:
    return await service.listar(session)


@router.post("", response_model=RespostaEstabelecimento, status_code=201)
async def criar_estabelecimento(
    body: CriarEstabelecimento, session: AsyncSession = Depends(get_db)
) -> Estabelecimento:
    return await service.criar(session, body)


@router.get("/{estabelecimento_id}", response_model=RespostaEstabelecimento)
async def obter_estabelecimento(
    estabelecimento_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> Estabelecimento:
    return await service.obter(session, estabelecimento_id)


@router.put("/{estabelecimento_id}", response_model=RespostaEstabelecimento)
async def atualizar_estabelecimento(
    estabelecimento_id: uuid.UUID,
    body: AtualizarEstabelecimento,
    session: AsyncSession = Depends(get_db),
) -> Estabelecimento:
    return await service.atualizar(session, estabelecimento_id, body)


@router.delete("/{estabelecimento_id}", status_code=204)
async def excluir_estabelecimento(
    estabelecimento_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> None:
    await service.excluir(session, estabelecimento_id)
