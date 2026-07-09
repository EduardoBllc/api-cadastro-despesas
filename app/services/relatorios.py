from __future__ import annotations

import uuid  # noqa: TC003
from datetime import date
from decimal import ROUND_HALF_DOWN, Decimal
from typing import TYPE_CHECKING

from sqlalchemy import extract, func, select
from sqlalchemy.orm import selectinload

from app.models import Abastecimento, CategoriaDespesa, Despesa
from app.schemas.relatorio import (
    AbastecimentoEficiencia,
    AbastecimentoMensal,
    GastoCategoria,
    GastoMensal,
)
from app.services.abastecimentos import _km_anterior

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def gastos_mensais(session: AsyncSession, ano: int) -> list[GastoMensal]:
    result = await session.execute(
        select(
            extract("month", Despesa.data_despesa).label("mes"),
            func.sum(Despesa.valor_total).label("total"),
            func.count(Despesa.id).label("quantidade"),
        )
        .where(extract("year", Despesa.data_despesa) == ano)
        .group_by(extract("month", Despesa.data_despesa))
        .order_by(extract("month", Despesa.data_despesa))
    )
    return [
        GastoMensal(mes=int(row.mes), total=row.total, quantidade=row.quantidade)
        for row in result.all()
    ]


async def gastos_por_categoria(
    session: AsyncSession, ano: int, mes: int | None
) -> list[GastoCategoria]:
    q = (
        select(
            Despesa.categoria_despesa_id,
            CategoriaDespesa.descricao.label("categoria_descricao"),
            func.sum(Despesa.valor_total).label("total"),
            func.count(Despesa.id).label("quantidade"),
        )
        .join(CategoriaDespesa, Despesa.categoria_despesa_id == CategoriaDespesa.id)
        .where(extract("year", Despesa.data_despesa) == ano)
        .group_by(Despesa.categoria_despesa_id, CategoriaDespesa.descricao)
        .order_by(func.sum(Despesa.valor_total).desc())
    )
    if mes is not None:
        q = q.where(extract("month", Despesa.data_despesa) == mes)
    rows = (await session.execute(q)).all()
    total_geral = sum((row.total for row in rows), Decimal("0")) or Decimal("1")
    return [
        GastoCategoria(
            categoria_id=row.categoria_despesa_id,
            categoria_descricao=row.categoria_descricao,
            total=row.total,
            quantidade=row.quantidade,
            percentual=(row.total / total_geral * 100).quantize(
                Decimal("0.1"), ROUND_HALF_DOWN
            ),
        )
        for row in rows
    ]


async def gastos_mensais_por_categoria(
    session: AsyncSession, ano: int, categoria_despesa_id: uuid.UUID
) -> list[GastoMensal]:
    result = await session.execute(
        select(
            extract("month", Despesa.data_despesa).label("mes"),
            func.sum(Despesa.valor_total).label("total"),
            func.count(Despesa.id).label("quantidade"),
        )
        .where(
            extract("year", Despesa.data_despesa) == ano,
            Despesa.categoria_despesa_id == categoria_despesa_id,
        )
        .group_by(extract("month", Despesa.data_despesa))
        .order_by(extract("month", Despesa.data_despesa))
    )
    return [
        GastoMensal(
            mes=int(row.mes),
            total=row.total,
            quantidade=row.quantidade,
            ticket_medio=(row.total / row.quantidade).quantize(Decimal("0.01"), ROUND_HALF_DOWN)
            if row.quantidade
            else None,
        )
        for row in result.all()
    ]


async def abastecimentos_mensais(
    session: AsyncSession, ano: int, carro_id: uuid.UUID | None
) -> list[AbastecimentoMensal]:
    q = (
        select(
            extract("month", Abastecimento.data_abastecimento).label("mes"),
            func.sum(Despesa.valor_total).label("total_gasto"),
            func.sum(Abastecimento.litros).label("total_litros"),
            func.count(Abastecimento.id).label("quantidade"),
        )
        .join(Despesa, Abastecimento.despesa_id == Despesa.id)
        .where(extract("year", Abastecimento.data_abastecimento) == ano)
        .group_by(extract("month", Abastecimento.data_abastecimento))
        .order_by(extract("month", Abastecimento.data_abastecimento))
    )
    if carro_id is not None:
        q = q.where(Abastecimento.carro_id == carro_id)
    return [
        AbastecimentoMensal(
            mes=int(row.mes),
            total_gasto=row.total_gasto,
            total_litros=row.total_litros,
            quantidade=row.quantidade,
        )
        for row in (await session.execute(q)).all()
    ]


async def abastecimentos_eficiencia(
    session: AsyncSession, carro_id: uuid.UUID | None, limite: int
) -> list[AbastecimentoEficiencia]:
    q = (
        select(Abastecimento)
        .options(selectinload(Abastecimento.despesa))
        .order_by(Abastecimento.data_abastecimento.desc())
        .limit(limite)
    )
    if carro_id is not None:
        q = q.where(Abastecimento.carro_id == carro_id)
    abastecimentos = list((await session.execute(q)).scalars().all())
    items = []
    for a in reversed(abastecimentos):
        km_ant = await _km_anterior(session, a.carro_id, a.quilometragem)
        km_rodados: int | None = None
        km_por_litro: Decimal | None = None
        if km_ant is not None:
            km_rodados = a.quilometragem - km_ant
            km_por_litro = (Decimal(km_rodados) / a.litros).quantize(
                Decimal("0.00"), ROUND_HALF_DOWN
            )
        items.append(
            AbastecimentoEficiencia(
                data_abastecimento=a.data_abastecimento,
                quilometragem=a.quilometragem,
                km_rodados=km_rodados,
                km_por_litro=km_por_litro,
                valor_por_litro=(a.despesa.valor_total / a.litros).quantize(
                    Decimal("0.00"), ROUND_HALF_DOWN
                ),
                total_gasto=a.despesa.valor_total,
            )
        )
    return items
