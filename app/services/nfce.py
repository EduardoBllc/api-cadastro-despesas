"""Importação de NFC-e: validação do link, busca na SEFAZ RS e montagem do rascunho."""

from __future__ import annotations

import re
from enum import StrEnum
from urllib.parse import parse_qs, urlsplit

import httpx
from fastapi import HTTPException, status

URL_CONSULTA_SEFAZ_RS = "https://dfe-portal.svrs.rs.gov.br/Dfe/QrCodeNFce"
TIMEOUT_SEFAZ_SEGUNDOS = 10.0
TAMANHO_CNPJ_RAIZ = 8
PARAMETRO_QR = "p"
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
