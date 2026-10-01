from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import status

from app.services.nfce import TAMANHO_CNPJ_RAIZ, ErroNfce

if TYPE_CHECKING:
    from httpx import AsyncClient

CODIGO_CENOURA = "162558"
CODIGO_ALFACE = "879495"
DATA_NOTA = "2026-08-19"
SUFIXO_OUTRA_FILIAL = "999999"


async def _novo_estabelecimento(client: AsyncClient, tipo_id: str) -> str:
    r = await client.post(
        "/estabelecimentos", json={"descricao": f"Filial {uuid.uuid4()}", "tipo_id": tipo_id}
    )
    assert r.status_code == status.HTTP_201_CREATED
    return r.json()["id"]


async def _novo_item(client: AsyncClient, categoria_item_id: str) -> str:
    r = await client.post(
        "/itens",
        json={"descricao": f"Item {uuid.uuid4()}", "categoria_item_id": categoria_item_id},
    )
    assert r.status_code == status.HTTP_201_CREATED
    return r.json()["id"]


def _payload(
    nota, estabelecimento_id: str, categoria_despesa_id: str, linhas: list[tuple[str, str]]
) -> dict:
    """linhas = [(codigo_produto_nfce, item_id), ...]"""
    return {
        "estabelecimento_id": estabelecimento_id,
        "categoria_despesa_id": categoria_despesa_id,
        "valor_total": "10.00",
        "data_despesa": DATA_NOTA,
        "nfce": {"chave": nota.chave, "cnpj": nota.cnpj},
        "itens": [
            {
                "item_id": item_id,
                "quantidade": "1",
                "valor_unitario": "5.00",
                "codigo_produto_nfce": codigo,
            }
            for codigo, item_id in linhas
        ],
    }


async def _importar(client: AsyncClient, sefaz, nota) -> dict:
    sefaz(nota.html)
    r = await client.post("/nfce/importar", json={"url": nota.url})
    assert r.status_code == status.HTTP_200_OK, r.text
    return r.json()


async def test_salvar_grava_chave_cnpj_e_vinculos(
    client: AsyncClient,
    tipo_estabelecimento_id: str,
    categoria_despesa_id: str,
    item_id: str,
    gerar_nota,
    sefaz,
) -> None:
    est = await _novo_estabelecimento(client, tipo_estabelecimento_id)
    nota = gerar_nota()
    r = await client.post(
        "/despesas", json=_payload(nota, est, categoria_despesa_id, [(CODIGO_CENOURA, item_id)])
    )
    assert r.status_code == status.HTTP_201_CREATED, r.text

    sefaz(nota.html)
    repetida = await client.post("/nfce/importar", json={"url": nota.url})
    assert repetida.status_code == status.HTTP_409_CONFLICT

    proxima = await _importar(client, sefaz, gerar_nota(cnpj=nota.cnpj))
    assert proxima["estabelecimento_id"] == est
    assert proxima["itens"][0]["item_id"] == item_id
    assert proxima["itens"][1]["item_id"] is None


async def test_vinculo_vale_para_outra_filial_da_rede(
    client: AsyncClient,
    tipo_estabelecimento_id: str,
    categoria_despesa_id: str,
    item_id: str,
    gerar_nota,
    sefaz,
) -> None:
    est = await _novo_estabelecimento(client, tipo_estabelecimento_id)
    nota = gerar_nota()
    await client.post(
        "/despesas", json=_payload(nota, est, categoria_despesa_id, [(CODIGO_CENOURA, item_id)])
    )

    outra_filial = nota.cnpj[:TAMANHO_CNPJ_RAIZ] + SUFIXO_OUTRA_FILIAL
    rascunho = await _importar(client, sefaz, gerar_nota(cnpj=outra_filial))

    assert rascunho["estabelecimento_id"] is None
    assert rascunho["itens"][0]["item_id"] == item_id


async def test_salvar_nota_duplicada_retorna_409(
    client: AsyncClient,
    tipo_estabelecimento_id: str,
    categoria_despesa_id: str,
    item_id: str,
    gerar_nota,
) -> None:
    est = await _novo_estabelecimento(client, tipo_estabelecimento_id)
    payload = _payload(gerar_nota(), est, categoria_despesa_id, [(CODIGO_CENOURA, item_id)])
    assert (await client.post("/despesas", json=payload)).status_code == status.HTTP_201_CREATED

    r = await client.post("/despesas", json=payload)

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == ErroNfce.JA_IMPORTADA.format(data="19/08/2026")


async def test_cnpj_passa_para_o_ultimo_estabelecimento_escolhido(
    client: AsyncClient,
    tipo_estabelecimento_id: str,
    categoria_despesa_id: str,
    item_id: str,
    gerar_nota,
    sefaz,
) -> None:
    primeiro = await _novo_estabelecimento(client, tipo_estabelecimento_id)
    segundo = await _novo_estabelecimento(client, tipo_estabelecimento_id)
    nota = gerar_nota()
    await client.post(
        "/despesas",
        json=_payload(nota, primeiro, categoria_despesa_id, [(CODIGO_CENOURA, item_id)]),
    )
    nota2 = gerar_nota(cnpj=nota.cnpj)
    r = await client.post(
        "/despesas",
        json=_payload(nota2, segundo, categoria_despesa_id, [(CODIGO_CENOURA, item_id)]),
    )
    assert r.status_code == status.HTTP_201_CREATED, r.text

    rascunho = await _importar(client, sefaz, gerar_nota(cnpj=nota.cnpj))

    assert rascunho["estabelecimento_id"] == segundo


async def test_ultima_escolha_do_vinculo_vence(
    client: AsyncClient,
    tipo_estabelecimento_id: str,
    categoria_despesa_id: str,
    categoria_item_id: str,
    gerar_nota,
    sefaz,
) -> None:
    est = await _novo_estabelecimento(client, tipo_estabelecimento_id)
    errado = await _novo_item(client, categoria_item_id)
    certo = await _novo_item(client, categoria_item_id)
    nota = gerar_nota()
    await client.post(
        "/despesas", json=_payload(nota, est, categoria_despesa_id, [(CODIGO_CENOURA, errado)])
    )
    nota2 = gerar_nota(cnpj=nota.cnpj)
    await client.post(
        "/despesas", json=_payload(nota2, est, categoria_despesa_id, [(CODIGO_CENOURA, certo)])
    )

    rascunho = await _importar(client, sefaz, gerar_nota(cnpj=nota.cnpj))

    assert rascunho["itens"][0]["item_id"] == certo


async def test_mesmo_codigo_em_duas_linhas_da_nota(
    client: AsyncClient,
    tipo_estabelecimento_id: str,
    categoria_despesa_id: str,
    item_id: str,
    gerar_nota,
) -> None:
    est = await _novo_estabelecimento(client, tipo_estabelecimento_id)
    linhas = [(CODIGO_ALFACE, item_id), (CODIGO_ALFACE, item_id)]

    r = await client.post(
        "/despesas", json=_payload(gerar_nota(), est, categoria_despesa_id, linhas)
    )

    assert r.status_code == status.HTTP_201_CREATED, r.text
    assert len(r.json()["itens"]) == len(linhas)
