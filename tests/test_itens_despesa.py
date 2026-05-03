from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient


def url(despesa_id: str, item_id: str | None = None) -> str:
    base = f"/despesas/{despesa_id}/itens"
    return f"{base}/{item_id}" if item_id else base


async def test_criar_item(
    client: AsyncClient, despesa_fixture: dict, categoria_item_id: str
) -> None:
    despesa_id = despesa_fixture["id"]
    r = await client.post(
        url(despesa_id),
        json={
            "descricao": "Arroz",
            "categoria_item_id": categoria_item_id,
            "quantidade": "2.00",
            "valor_unitario": "10.00",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["descricao"] == "Arroz"
    assert data["despesa_id"] == despesa_id
    assert "id" in data
    assert "data_cadastro" in data


async def test_criar_item_calcula_valor_total(
    client: AsyncClient, despesa_fixture: dict, categoria_item_id: str
) -> None:
    despesa_id = despesa_fixture["id"]
    r = await client.post(
        url(despesa_id),
        json={
            "descricao": "Feijão",
            "categoria_item_id": categoria_item_id,
            "quantidade": "3.00",
            "valor_unitario": "8.00",
        },
    )
    assert r.status_code == 201
    assert float(r.json()["valor_total"]) == 24.0


async def test_criar_item_despesa_inexistente_retorna_404(
    client: AsyncClient, categoria_item_id: str
) -> None:
    r = await client.post(
        url(str(uuid.uuid4())),
        json={
            "descricao": "X",
            "categoria_item_id": categoria_item_id,
            "quantidade": "1.00",
            "valor_unitario": "1.00",
        },
    )
    assert r.status_code == 404


async def test_criar_item_quantidade_zero_retorna_422(
    client: AsyncClient, despesa_fixture: dict, categoria_item_id: str
) -> None:
    r = await client.post(
        url(despesa_fixture["id"]),
        json={
            "descricao": "X",
            "categoria_item_id": categoria_item_id,
            "quantidade": "0.00",
            "valor_unitario": "1.00",
        },
    )
    assert r.status_code == 422


async def test_criar_item_valor_unitario_negativo_retorna_422(
    client: AsyncClient, despesa_fixture: dict, categoria_item_id: str
) -> None:
    r = await client.post(
        url(despesa_fixture["id"]),
        json={
            "descricao": "X",
            "categoria_item_id": categoria_item_id,
            "quantidade": "1.00",
            "valor_unitario": "-5.00",
        },
    )
    assert r.status_code == 422


async def test_listar_itens(
    client: AsyncClient, despesa_fixture: dict, categoria_item_id: str
) -> None:
    despesa_id = despesa_fixture["id"]
    r = await client.get(url(despesa_id))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_listar_itens_despesa_inexistente_retorna_404(client: AsyncClient) -> None:
    r = await client.get(url(str(uuid.uuid4())))
    assert r.status_code == 404


async def test_obter_item(
    client: AsyncClient, despesa_fixture: dict, categoria_item_id: str
) -> None:
    despesa_id = despesa_fixture["id"]
    r_criacao = await client.post(
        url(despesa_id),
        json={
            "descricao": "Óleo",
            "categoria_item_id": categoria_item_id,
            "quantidade": "1.00",
            "valor_unitario": "9.00",
        },
    )
    item_id = r_criacao.json()["id"]

    r = await client.get(url(despesa_id, item_id))
    assert r.status_code == 200
    assert r.json()["id"] == item_id
    assert r.json()["descricao"] == "Óleo"
    assert float(r.json()["valor_total"]) == 9.0


async def test_obter_item_inexistente_retorna_404(
    client: AsyncClient, despesa_fixture: dict
) -> None:
    r = await client.get(url(despesa_fixture["id"], str(uuid.uuid4())))
    assert r.status_code == 404


async def test_atualizar_item(
    client: AsyncClient, despesa_fixture: dict, categoria_item_id: str
) -> None:
    despesa_id = despesa_fixture["id"]
    r_criacao = await client.post(
        url(despesa_id),
        json={
            "descricao": "Leite",
            "categoria_item_id": categoria_item_id,
            "quantidade": "2.00",
            "valor_unitario": "5.00",
        },
    )
    item_id = r_criacao.json()["id"]

    r = await client.put(url(despesa_id, item_id), json={"descricao": "Leite Integral"})
    assert r.status_code == 200
    assert r.json()["id"] == item_id
    assert r.json()["descricao"] == "Leite Integral"


async def test_atualizar_item_recalcula_valor_total(
    client: AsyncClient, despesa_fixture: dict, categoria_item_id: str
) -> None:
    despesa_id = despesa_fixture["id"]
    r_criacao = await client.post(
        url(despesa_id),
        json={
            "descricao": "Manteiga",
            "categoria_item_id": categoria_item_id,
            "quantidade": "1.00",
            "valor_unitario": "12.00",
        },
    )
    item_id = r_criacao.json()["id"]
    assert float(r_criacao.json()["valor_total"]) == 12.0

    r = await client.put(url(despesa_id, item_id), json={"quantidade": "3.00"})
    assert r.status_code == 200
    assert float(r.json()["valor_total"]) == 36.0


async def test_atualizar_item_inexistente_retorna_404(
    client: AsyncClient, despesa_fixture: dict
) -> None:
    r = await client.put(url(despesa_fixture["id"], str(uuid.uuid4())), json={"descricao": "X"})
    assert r.status_code == 404


async def test_excluir_item(
    client: AsyncClient, despesa_fixture: dict, categoria_item_id: str
) -> None:
    despesa_id = despesa_fixture["id"]
    r_criacao = await client.post(
        url(despesa_id),
        json={
            "descricao": "Para Excluir",
            "categoria_item_id": categoria_item_id,
            "quantidade": "1.00",
            "valor_unitario": "1.00",
        },
    )
    item_id = r_criacao.json()["id"]

    r = await client.delete(url(despesa_id, item_id))
    assert r.status_code == 204

    r = await client.get(url(despesa_id, item_id))
    assert r.status_code == 404


async def test_excluir_item_inexistente_retorna_404(
    client: AsyncClient, despesa_fixture: dict
) -> None:
    r = await client.delete(url(despesa_fixture["id"], str(uuid.uuid4())))
    assert r.status_code == 404


async def test_despesa_exibe_itens_apos_insercao(
    client: AsyncClient, categoria_despesa_id: str, categoria_item_id: str, estabelecimento_id: str
) -> None:
    r_despesa = await client.post(
        "/despesas",
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "50.00",
        },
    )
    despesa_id = r_despesa.json()["id"]

    await client.post(
        url(despesa_id),
        json={
            "descricao": "Sabão",
            "categoria_item_id": categoria_item_id,
            "quantidade": "2.00",
            "valor_unitario": "7.50",
        },
    )

    r = await client.get(f"/despesas/{despesa_id}")
    assert r.status_code == 200
    itens = r.json()["itens"]
    assert len(itens) == 1
    assert itens[0]["descricao"] == "Sabão"
    assert float(itens[0]["valor_total"]) == 15.0
