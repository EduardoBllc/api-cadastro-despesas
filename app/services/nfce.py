"""Importação de NFC-e: validação do link, busca na SEFAZ RS e montagem do rascunho."""

from __future__ import annotations

import re
import uuid
from enum import StrEnum
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlsplit

import httpx
from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models import Despesa, Estabelecimento, VinculoProdutoNfce
from app.schemas.nfce import ItemRascunhoNfce, RascunhoNfce
from app.services.nfce_parser import NotaInvalidaError, parse, ratear_desconto

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas.item_despesa import CriarItemDespesaNfce
    from app.schemas.nfce import OrigemNfce

URL_CONSULTA_SEFAZ_RS = "https://dfe-portal.svrs.rs.gov.br/Dfe/QrCodeNFce"
TIMEOUT_SEFAZ_SEGUNDOS = 10.0
TAMANHO_CNPJ_RAIZ = 8
PARAMETRO_QR = "p"
FORMATO_DATA_BR = "%d/%m/%Y"
# chave de 44 dígitos do RS (UF 43) seguida dos campos do QR separados por "|"
_FORMATO_P = re.compile(r"43\d{42}(\|[0-9A-Za-z.]+)+")


class ErroNfce(StrEnum):
    LINK_INVALIDO = "Link de NFC-e inválido (somente RS)"
    SEFAZ_INDISPONIVEL = "SEFAZ indisponível, tente novamente"
    FORMATO_DESCONHECIDO = "Nota não encontrada ou formato desconhecido"
    JA_IMPORTADA = "Nota já importada (despesa de {data})"


def extrair_parametro(url: str) -> str:
    valores = parse_qs(urlsplit(url.strip()).query).get(PARAMETRO_QR, [])
    p = valores[0] if valores else ""
    if not _FORMATO_P.fullmatch(p):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=ErroNfce.LINK_INVALIDO
        )
    return p


async def buscar_html(p: str, transport: httpx.AsyncBaseTransport | None = None) -> str:
    try:
        async with httpx.AsyncClient(
            timeout=TIMEOUT_SEFAZ_SEGUNDOS, follow_redirects=True, transport=transport
        ) as client:
            resposta = await client.get(URL_CONSULTA_SEFAZ_RS, params={PARAMETRO_QR: p})
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=ErroNfce.SEFAZ_INDISPONIVEL
        ) from exc
    if resposta.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=ErroNfce.SEFAZ_INDISPONIVEL
        )
    return resposta.text


async def garantir_nao_importada(session: AsyncSession, chave: str) -> None:
    data = await session.scalar(select(Despesa.data_despesa).where(Despesa.chave_nfce == chave))
    if data is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ErroNfce.JA_IMPORTADA.format(data=data.strftime(FORMATO_DATA_BR)),
        )


async def importar(session: AsyncSession, url: str) -> RascunhoNfce:
    p = extrair_parametro(url)
    html = await buscar_html(p)
    try:
        nota = parse(html)
    except NotaInvalidaError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=ErroNfce.FORMATO_DESCONHECIDO,
        ) from exc
    await garantir_nao_importada(session, nota.chave)

    estabelecimento_id = await session.scalar(
        select(Estabelecimento.id).where(Estabelecimento.cnpj == nota.cnpj)
    )
    resultado = await session.execute(
        select(VinculoProdutoNfce.codigo_produto, VinculoProdutoNfce.item_id).where(
            VinculoProdutoNfce.cnpj_raiz == nota.cnpj[:TAMANHO_CNPJ_RAIZ],
            VinculoProdutoNfce.codigo_produto.in_([i.codigo for i in nota.itens]),
        )
    )
    vinculos = dict(resultado.tuples().all())
    descontos = ratear_desconto(nota.itens, nota.desconto, nota.valor_pago)

    return RascunhoNfce(
        chave=nota.chave,
        data_emissao=nota.data_emissao,
        cnpj=nota.cnpj,
        razao_social=nota.razao_social,
        endereco=nota.endereco,
        estabelecimento_id=estabelecimento_id,
        valor_pago=nota.valor_pago,
        desconto_total=nota.desconto,
        itens=[
            ItemRascunhoNfce(
                codigo=item.codigo,
                descricao_nota=item.descricao,
                unidade_nota=item.unidade,
                quantidade=item.quantidade,
                valor_unitario=item.valor_unitario,
                valor_desconto=desconto,
                item_id=vinculos.get(item.codigo),
            )
            for item, desconto in zip(nota.itens, descontos, strict=True)
        ],
    )


async def registrar_origem(
    session: AsyncSession,
    origem: OrigemNfce,
    estabelecimento_id: uuid.UUID,
    itens: list[CriarItemDespesaNfce],
) -> None:
    """Grava CNPJ no estabelecimento escolhido e os vínculos código → item (última escolha vence)."""
    await session.execute(
        update(Estabelecimento)
        .where(Estabelecimento.cnpj == origem.cnpj, Estabelecimento.id != estabelecimento_id)
        .values(cnpj=None)
    )
    await session.execute(
        update(Estabelecimento)
        .where(Estabelecimento.id == estabelecimento_id)
        .values(cnpj=origem.cnpj)
    )

    # dict deduplica códigos repetidos na nota: o upsert não pode tocar a mesma linha duas vezes
    vinculos = {i.codigo_produto_nfce: i.item_id for i in itens if i.codigo_produto_nfce}
    if not vinculos:
        return
    insercao = pg_insert(VinculoProdutoNfce).values(
        [
            {
                "id": uuid.uuid4(),
                "cnpj_raiz": origem.cnpj[:TAMANHO_CNPJ_RAIZ],
                "codigo_produto": codigo,
                "item_id": item_id,
            }
            for codigo, item_id in vinculos.items()
        ]
    )
    await session.execute(
        insercao.on_conflict_do_update(
            index_elements=[VinculoProdutoNfce.cnpj_raiz, VinculoProdutoNfce.codigo_produto],
            set_={"item_id": insercao.excluded.item_id, "data_alteracao": func.now()},
        )
    )
