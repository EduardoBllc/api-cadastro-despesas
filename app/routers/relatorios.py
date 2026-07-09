from __future__ import annotations

import uuid  # noqa: TC003
from datetime import date
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Query

from app.database import get_db
from app.schemas.relatorio import (
    AbastecimentoEficiencia,
    AbastecimentoMensal,
    GastoCategoria,
    GastoMensal,
)
from app.services import relatorios as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/relatorios", tags=["relatorios"])


@router.get("/gastos-mensais", response_model=list[GastoMensal])
async def gastos_mensais(
    session: AsyncSession = Depends(get_db),
    ano: int | None = Query(None),
) -> list[GastoMensal]:
    return await service.gastos_mensais(session, ano or date.today().year)


@router.get("/gastos-por-categoria", response_model=list[GastoCategoria])
async def gastos_por_categoria(
    session: AsyncSession = Depends(get_db),
    ano: int | None = Query(None),
    mes: int | None = Query(None, ge=1, le=12),
) -> list[GastoCategoria]:
    return await service.gastos_por_categoria(session, ano or date.today().year, mes)


@router.get("/gastos-mensais-por-categoria", response_model=list[GastoMensal])
async def gastos_mensais_por_categoria(
    categoria_despesa_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    ano: int | None = Query(None),
) -> list[GastoMensal]:
    return await service.gastos_mensais_por_categoria(
        session, ano or date.today().year, categoria_despesa_id
    )


@router.get("/abastecimentos-mensais", response_model=list[AbastecimentoMensal])
async def abastecimentos_mensais(
    session: AsyncSession = Depends(get_db),
    ano: int | None = Query(None),
    carro_id: uuid.UUID | None = Query(None),
) -> list[AbastecimentoMensal]:
    return await service.abastecimentos_mensais(session, ano or date.today().year, carro_id)


@router.get("/abastecimentos-eficiencia", response_model=list[AbastecimentoEficiencia])
async def abastecimentos_eficiencia(
    session: AsyncSession = Depends(get_db),
    carro_id: uuid.UUID | None = Query(None),
    limite: int = Query(20, ge=1, le=100),
) -> list[AbastecimentoEficiencia]:
    return await service.abastecimentos_eficiencia(session, carro_id, limite)
