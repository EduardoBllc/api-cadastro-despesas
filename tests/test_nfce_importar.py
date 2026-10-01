from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from sqlalchemy import update

from app.database import build_session_factory
from app.models import Despesa, Estabelecimento, VinculoProdutoNfce
from app.services import nfce as nfce_service
from app.services.nfce import TAMANHO_CNPJ_RAIZ, ErroNfce

if TYPE_CHECKING:
    import pytest
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncEngine

PREFIX = "/nfce/importar"
CODIGO_CENOURA = "162558"
DATA_NOTA = "2026-08-19"


async def _novo_estabelecimento(client: AsyncClient, tipo_id: str) -> str:
    r = await client.post(
        "/estabelecimentos", json={"descricao": f"Filial {uuid.uuid4()}", "tipo_id": tipo_id}
    )
    assert r.status_code == status.HTTP_201_CREATED
    return r.json()["id"]


async def test_importa_nota_sem_vinculos(client: AsyncClient, gerar_nota, sefaz) -> None:
    nota = gerar_nota()
    sefaz(nota.html)

    r = await client.post(PREFIX, json={"url": nota.url})

    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["chave"] == nota.chave
    assert data["cnpj"] == nota.cnpj
    assert data["razao_social"] == "Irmaos Andreazza Ltda"
    assert data["endereco"] == "Rua Padre Angelo Tronca, 2150, Sao Luiz, Caxias Do Sul, RS"
    assert data["data_emissao"] == DATA_NOTA
    assert data["estabelecimento_id"] is None
    assert data["valor_pago"] == "131.85"
    assert data["desconto_total"] == "14.65"
    assert len(data["itens"]) == 14
    assert data["itens"][0] == {
        "codigo": CODIGO_CENOURA,
        "descricao_nota": "Cenoura Kg",
        "unidade_nota": "KG",
        "quantidade": "1.250",
        "valor_unitario": "8.99",
        "valor_desconto": "0.90",
        "item_id": None,
    }


async def test_resolve_estabelecimento_e_itens_vinculados(
    client: AsyncClient,
    db_engine: AsyncEngine,
    tipo_estabelecimento_id: str,
    item_id: str,
    gerar_nota,
    sefaz,
) -> None:
    nota = gerar_nota()
    estabelecimento_id = await _novo_estabelecimento(client, tipo_estabelecimento_id)
    async with build_session_factory(db_engine)() as session:
        await session.execute(
            update(Estabelecimento)
            .where(Estabelecimento.id == uuid.UUID(estabelecimento_id))
            .values(cnpj=nota.cnpj)
        )
        session.add(
            VinculoProdutoNfce(
                cnpj_raiz=nota.cnpj[:TAMANHO_CNPJ_RAIZ],
                codigo_produto=CODIGO_CENOURA,
                item_id=uuid.UUID(item_id),
            )
        )
        await session.commit()
    sefaz(nota.html)

    data = (await client.post(PREFIX, json={"url": nota.url})).json()

    assert data["estabelecimento_id"] == estabelecimento_id
    assert data["itens"][0]["item_id"] == item_id
    assert data["itens"][1]["item_id"] is None


async def test_link_invalido_retorna_422(client: AsyncClient) -> None:
    r = await client.post(PREFIX, json={"url": "https://exemplo.com/?p=123"})
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert r.json()["detail"] == ErroNfce.LINK_INVALIDO


async def test_pagina_sem_nota_retorna_422(client: AsyncClient, gerar_nota, sefaz) -> None:
    nota = gerar_nota()
    sefaz("<html><body>Nota não encontrada</body></html>")
    r = await client.post(PREFIX, json={"url": nota.url})
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert r.json()["detail"] == ErroNfce.FORMATO_DESCONHECIDO


async def test_sefaz_indisponivel_retorna_502(
    client: AsyncClient, gerar_nota, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _fora_do_ar(p: str) -> str:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=ErroNfce.SEFAZ_INDISPONIVEL
        )

    monkeypatch.setattr(nfce_service, "buscar_html", _fora_do_ar)
    r = await client.post(PREFIX, json={"url": gerar_nota().url})
    assert r.status_code == status.HTTP_502_BAD_GATEWAY
    assert r.json()["detail"] == ErroNfce.SEFAZ_INDISPONIVEL


async def test_nota_ja_importada_retorna_409(
    client: AsyncClient,
    db_engine: AsyncEngine,
    categoria_despesa_id: str,
    estabelecimento_id: str,
    gerar_nota,
    sefaz,
) -> None:
    nota = gerar_nota()
    r = await client.post(
        "/despesas",
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "131.85",
            "data_despesa": DATA_NOTA,
        },
    )
    async with build_session_factory(db_engine)() as session:
        await session.execute(
            update(Despesa)
            .where(Despesa.id == uuid.UUID(r.json()["id"]))
            .values(chave_nfce=nota.chave)
        )
        await session.commit()
    sefaz(nota.html)

    r = await client.post(PREFIX, json={"url": nota.url})

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == ErroNfce.JA_IMPORTADA.format(data="19/08/2026")
