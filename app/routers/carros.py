from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas import AtualizarCarro, CriarCarro, RespostaCarro
from app.services import carros as service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import Carro

router = APIRouter(prefix="/carros", tags=["carros"])


@router.get("", response_model=list[RespostaCarro])
async def listar_carros(session: AsyncSession = Depends(get_db)) -> list[Carro]:
    return await service.listar(session)


@router.post("", response_model=RespostaCarro, status_code=201)
async def criar_carro(body: CriarCarro, session: AsyncSession = Depends(get_db)) -> Carro:
    return await service.criar(session, body)


@router.get("/{carro_id}", response_model=RespostaCarro)
async def obter_carro(carro_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> Carro:
    return await service.obter(session, carro_id)


@router.put("/{carro_id}", response_model=RespostaCarro)
async def atualizar_carro(
    carro_id: uuid.UUID, body: AtualizarCarro, session: AsyncSession = Depends(get_db)
) -> Carro:
    return await service.atualizar(session, carro_id, body)


@router.delete("/{carro_id}", status_code=204)
async def excluir_carro(carro_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> None:
    await service.excluir(session, carro_id)
