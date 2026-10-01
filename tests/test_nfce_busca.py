from __future__ import annotations

import httpx
import pytest
from fastapi import HTTPException, status

from app.services.nfce import (
    URL_CONSULTA_SEFAZ_RS,
    ErroNfce,
    buscar_html,
    extrair_parametro,
)

CHAVE = "43" + "0" * 41 + "1"
P_VALIDO = f"{CHAVE}|2|1|2|{'A' * 40}"
URL_VALIDA = f"https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p={P_VALIDO}"


def test_extrai_p_da_url_do_qr() -> None:
    assert extrair_parametro(URL_VALIDA) == P_VALIDO


def test_aceita_barras_codificadas_e_espacos() -> None:
    url = f"  {URL_VALIDA.replace('|', '%7C')}  "
    assert extrair_parametro(url) == P_VALIDO


@pytest.mark.parametrize(
    "url",
    [
        URL_VALIDA.replace("p=43", "p=35"),  # chave de SP
        "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx",  # sem p
        "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=abc",  # malformado
        f"https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p={CHAVE}",  # só a chave
    ],
)
def test_rejeita_link_invalido(url: str) -> None:
    with pytest.raises(HTTPException) as erro:
        extrair_parametro(url)
    assert erro.value.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert erro.value.detail == ErroNfce.LINK_INVALIDO


async def test_busca_na_url_constante_da_sefaz() -> None:
    def responder(request: httpx.Request) -> httpx.Response:
        assert str(request.url).startswith(URL_CONSULTA_SEFAZ_RS)
        assert request.url.params["p"] == P_VALIDO
        return httpx.Response(status.HTTP_200_OK, text="<html>ok</html>")

    html = await buscar_html(P_VALIDO, transport=httpx.MockTransport(responder))
    assert html == "<html>ok</html>"


async def test_timeout_vira_502() -> None:
    def responder(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timeout", request=request)

    with pytest.raises(HTTPException) as erro:
        await buscar_html(P_VALIDO, transport=httpx.MockTransport(responder))
    assert erro.value.status_code == status.HTTP_502_BAD_GATEWAY
    assert erro.value.detail == ErroNfce.SEFAZ_INDISPONIVEL


async def test_erro_5xx_vira_502() -> None:
    def responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status.HTTP_503_SERVICE_UNAVAILABLE)

    with pytest.raises(HTTPException) as erro:
        await buscar_html(P_VALIDO, transport=httpx.MockTransport(responder))
    assert erro.value.status_code == status.HTTP_502_BAD_GATEWAY
