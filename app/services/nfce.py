"""Importação de NFC-e: validação do link, busca na SEFAZ RS e montagem do rascunho."""

from __future__ import annotations

import re
from enum import StrEnum
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlsplit

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select

from app.models import Despesa, Estabelecimento, VinculoProdutoNfce
from app.schemas.nfce import ItemRascunhoNfce, RascunhoNfce
from app.services.nfce_parser import NotaInvalidaError, parse, ratear_desconto

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

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
