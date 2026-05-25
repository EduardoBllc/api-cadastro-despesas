from __future__ import annotations

import uuid  # noqa: TC003
from decimal import ROUND_HALF_DOWN, Decimal
from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models import Abastecimento
from app.schemas import RespostaAbastecimento, RespostaPaginadaAbastecimento

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def _km_anterior(
    session: AsyncSession, carro_id: uuid.UUID, quilometragem: int
) -> int | None:
    result = await session.execute(
        select(Abastecimento.quilometragem)
        .where(
            Abastecimento.carro_id == carro_id,
            Abastecimento.quilometragem < quilometragem,
        )
        .order_by(Abastecimento.quilometragem.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def build_resposta(
    session: AsyncSession, abastecimento: Abastecimento, valor_total: Decimal
) -> RespostaAbastecimento:
    km_ant = await _km_anterior(session, abastecimento.carro_id, abastecimento.quilometragem)
    km_rodados: int | None = None
    km_por_litro: Decimal | None = None
    if km_ant is not None:
        km_rodados = abastecimento.quilometragem - km_ant
        km_por_litro = (Decimal(km_rodados) / abastecimento.litros).quantize(
            Decimal("0.00"), ROUND_HALF_DOWN
        )
    return RespostaAbastecimento(
        id=abastecimento.id,
        despesa_id=abastecimento.despesa_id,
        carro_id=abastecimento.carro_id,
        data_abastecimento=abastecimento.data_abastecimento,
        quilometragem=abastecimento.quilometragem,
        litros=abastecimento.litros,
        valor_total=valor_total,
        valor_por_litro=valor_total / abastecimento.litros,
        km_rodados=km_rodados,
        km_por_litro=km_por_litro,
        posto_id=abastecimento.posto_id,
        observacao=abastecimento.observacao,
        data_cadastro=abastecimento.data_cadastro,
        data_alteracao=abastecimento.data_alteracao,
    )


async def listar(
    session: AsyncSession,
    carro_id: uuid.UUID | None,
    page: int,
    page_size: int,
) -> RespostaPaginadaAbastecimento:
    offset = (page - 1) * page_size
    base_filter = Abastecimento.carro_id == carro_id if carro_id is not None else None
    count_q = select(func.count(Abastecimento.id))
    list_q = (
        select(Abastecimento)
        .options(selectinload(Abastecimento.despesa))
        .order_by(Abastecimento.data_abastecimento.desc())
    )
    if base_filter is not None:
        count_q = count_q.where(base_filter)
        list_q = list_q.where(base_filter)
    total = await session.scalar(count_q)
    result = await session.execute(list_q.offset(offset).limit(page_size))
    abastecimentos = list(result.scalars().all())
    items = [await build_resposta(session, a, a.despesa.valor_total) for a in abastecimentos]
    return RespostaPaginadaAbastecimento(
        total=total or 0, page=page, page_size=page_size, items=items
    )
