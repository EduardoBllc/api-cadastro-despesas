from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas import AtualizarTipoEstabelecimento, CriarTipoEstabelecimento, RespostaTipoEstabelecimento
from app.services import tipos_estabelecimento as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import TipoEstabelecimento

router = APIRouter(prefix="/tipos-estabelecimento", tags=["tipos-estabelecimento"])


@router.get("", response_model=list[RespostaTipoEstabelecimento])
async def listar_tipos_estabelecimento(
    session: AsyncSession = Depends(get_db),
) -> list[TipoEstabelecimento]:
    return await service.listar(session)


@router.post("", response_model=RespostaTipoEstabelecimento, status_code=201)
async def criar_tipo_estabelecimento(
    body: CriarTipoEstabelecimento, session: AsyncSession = Depends(get_db)
) -> TipoEstabelecimento:
    return await service.criar(session, body)


@router.get("/{tipo_id}", response_model=RespostaTipoEstabelecimento)
async def obter_tipo_estabelecimento(
    tipo_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> TipoEstabelecimento:
    return await service.obter(session, tipo_id)


@router.put("/{tipo_id}", response_model=RespostaTipoEstabelecimento)
async def atualizar_tipo_estabelecimento(
    tipo_id: uuid.UUID,
    body: AtualizarTipoEstabelecimento,
    session: AsyncSession = Depends(get_db),
) -> TipoEstabelecimento:
    return await service.atualizar(session, tipo_id, body)


@router.delete("/{tipo_id}", status_code=204)
async def excluir_tipo_estabelecimento(
    tipo_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> None:
    await service.excluir(session, tipo_id)
