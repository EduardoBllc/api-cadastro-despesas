from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Query

from app.database import get_db
from app.schemas import (
    AtualizarAbastecimento,
    AtualizarDespesa,
    CriarAbastecimento,
    CriarDespesa,
    RespostaAbastecimento,
    RespostaDespesaDetalhe,
    RespostaPaginadaDespesa,
)
from app.services import despesas as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/despesas", tags=["despesas"])


@router.get("", response_model=RespostaPaginadaDespesa)
async def listar_despesas(
    session: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> RespostaPaginadaDespesa:
    return await service.listar(session, page, page_size)


@router.post("", response_model=RespostaDespesaDetalhe, status_code=201)
async def criar_despesa(
    body: CriarDespesa, session: AsyncSession = Depends(get_db)
) -> RespostaDespesaDetalhe:
    return await service.criar(session, body)


@router.get("/{despesa_id}", response_model=RespostaDespesaDetalhe)
async def obter_despesa(
    despesa_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> RespostaDespesaDetalhe:
    return await service.obter(session, despesa_id)


@router.put("/{despesa_id}", response_model=RespostaDespesaDetalhe)
async def atualizar_despesa(
    despesa_id: uuid.UUID, body: AtualizarDespesa, session: AsyncSession = Depends(get_db)
) -> RespostaDespesaDetalhe:
    return await service.atualizar(session, despesa_id, body)


@router.delete("/{despesa_id}", status_code=204)
async def excluir_despesa(despesa_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> None:
    await service.excluir(session, despesa_id)


# ── Abastecimento sub-resource ──────────────────────────────────────────────


@router.post(
    "/{despesa_id}/abastecimento",
    response_model=RespostaAbastecimento,
    status_code=201,
)
async def criar_abastecimento(
    despesa_id: uuid.UUID, body: CriarAbastecimento, session: AsyncSession = Depends(get_db)
) -> RespostaAbastecimento:
    return await service.criar_abastecimento(session, despesa_id, body)


@router.put("/{despesa_id}/abastecimento", response_model=RespostaAbastecimento)
async def atualizar_abastecimento(
    despesa_id: uuid.UUID,
    body: AtualizarAbastecimento,
    session: AsyncSession = Depends(get_db),
) -> RespostaAbastecimento:
    return await service.atualizar_abastecimento(session, despesa_id, body)


@router.delete("/{despesa_id}/abastecimento", status_code=204)
async def excluir_abastecimento(
    despesa_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> None:
    await service.excluir_abastecimento(session, despesa_id)
