from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas import AtualizarUnidadeMedida, CriarUnidadeMedida, RespostaUnidadeMedida
from app.services import unidades_medida as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import UnidadeMedida

router = APIRouter(prefix="/unidades-medida", tags=["unidades-medida"])


@router.get("", response_model=list[RespostaUnidadeMedida])
async def listar_unidades_medida(
    session: AsyncSession = Depends(get_db),
) -> list[UnidadeMedida]:
    return await service.listar(session)


@router.post("", response_model=RespostaUnidadeMedida, status_code=201)
async def criar_unidade_medida(
    body: CriarUnidadeMedida, session: AsyncSession = Depends(get_db)
) -> UnidadeMedida:
    return await service.criar(session, body)


@router.get("/{unidade_id}", response_model=RespostaUnidadeMedida)
async def obter_unidade_medida(
    unidade_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> UnidadeMedida:
    return await service.obter(session, unidade_id)


@router.put("/{unidade_id}", response_model=RespostaUnidadeMedida)
async def atualizar_unidade_medida(
    unidade_id: uuid.UUID,
    body: AtualizarUnidadeMedida,
    session: AsyncSession = Depends(get_db),
) -> UnidadeMedida:
    return await service.atualizar(session, unidade_id, body)


@router.delete("/{unidade_id}", status_code=204)
async def excluir_unidade_medida(
    unidade_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> None:
    await service.excluir(session, unidade_id)
