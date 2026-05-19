from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import desc, func, select

from app.models import CategoriaDespesa, CategoriaItem, Despesa, Estabelecimento, Item

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas.sugestoes import RespostaSugestoes, SugestaoCategoria


async def sugerir_categoria_despesa(session: AsyncSession, termo: str) -> RespostaSugestoes:
    # Busca despesas cujo estabelecimento tem nome similar
    # Agrupa por categoria e conta a frequência
    query = (
        select(
            CategoriaDespesa.id,
            CategoriaDespesa.descricao,
            func.count(Despesa.id).label("frequencia"),
        )
        .join(Despesa.categoria_despesa)
        .join(Despesa.estabelecimento)
        .where(Estabelecimento.descricao.ilike(f"%{termo}%"))
        .group_by(CategoriaDespesa.id, CategoriaDespesa.descricao)
        .order_by(desc("frequencia"))
        .limit(3)
    )

    result = await session.execute(query)
    rows = result.all()

    total = sum(row.frequencia for row in rows)
    sugestoes: list[SugestaoCategoria] = []

    for row in rows:
        sugestoes.append(
            {
                "id": row.id,
                "descricao": row.descricao,
                "confianca": round(row.frequencia / total, 2) if total > 0 else 0,
            }
        )

    return {"sugestoes": sugestoes}


async def sugerir_categoria_item(session: AsyncSession, termo: str) -> RespostaSugestoes:
    # Busca itens com descrição similar e agrupa por categoria
    query = (
        select(
            CategoriaItem.id,
            CategoriaItem.descricao,
            func.count(Item.id).label("frequencia"),
        )
        .join(Item.categoria_item)
        .where(Item.descricao.ilike(f"%{termo}%"))
        .group_by(CategoriaItem.id, CategoriaItem.descricao)
        .order_by(desc("frequencia"))
        .limit(3)
    )

    result = await session.execute(query)
    rows = result.all()

    total = sum(row.frequencia for row in rows)
    sugestoes = []

    for row in rows:
        sugestoes.append(
            {
                "id": row.id,
                "descricao": row.descricao,
                "confianca": round(row.frequencia / total, 2) if total > 0 else 0,
            }
        )

    return {"sugestoes": sugestoes}
