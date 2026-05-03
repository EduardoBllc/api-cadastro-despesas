from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient

PREFIX = "/carros"


async def test_listar_retorna_lista(client: AsyncClient) -> None:
    r = await client.get(PREFIX)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_criar(client: AsyncClient) -> None:
    r = await client.post(PREFIX, json={"nome": "Gol 2019", "placa": "BRA2E19"})
    assert r.status_code == 201
    data = r.json()
    assert data["nome"] == "Gol 2019"
    assert data["placa"] == "BRA2E19"
    assert data["ativo"] is True
    assert "id" in data
    assert "data_cadastro" in data
    assert "data_alteracao" in data


async def test_criar_sem_placa(client: AsyncClient) -> None:
    r = await client.post(PREFIX, json={"nome": "Moto Sem Placa"})
    assert r.status_code == 201
    assert r.json()["placa"] is None


async def test_criar_sem_nome_retorna_422(client: AsyncClient) -> None:
    r = await client.post(PREFIX, json={"placa": "AAA1111"})
    assert r.status_code == 422


async def test_criar_nome_muito_longo_retorna_422(client: AsyncClient) -> None:
    r = await client.post(PREFIX, json={"nome": "A" * 61})
    assert r.status_code == 422


async def test_obter(client: AsyncClient) -> None:
    r_criacao = await client.post(PREFIX, json={"nome": "Onix 2022"})
    id_ = r_criacao.json()["id"]

    r = await client.get(f"{PREFIX}/{id_}")
    assert r.status_code == 200
    assert r.json()["id"] == id_
    assert r.json()["nome"] == "Onix 2022"


async def test_obter_inexistente_retorna_404(client: AsyncClient) -> None:
    r = await client.get(f"{PREFIX}/{uuid.uuid4()}")
    assert r.status_code == 404


async def test_atualizar(client: AsyncClient) -> None:
    r_criacao = await client.post(PREFIX, json={"nome": "Carro Antes"})
    id_ = r_criacao.json()["id"]

    r = await client.put(f"{PREFIX}/{id_}", json={"nome": "Carro Depois", "ativo": False})
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == id_
    assert data["nome"] == "Carro Depois"
    assert data["ativo"] is False


async def test_atualizar_inexistente_retorna_404(client: AsyncClient) -> None:
    r = await client.put(f"{PREFIX}/{uuid.uuid4()}", json={"nome": "X"})
    assert r.status_code == 404


async def test_excluir(client: AsyncClient) -> None:
    r_criacao = await client.post(PREFIX, json={"nome": "Para Excluir"})
    id_ = r_criacao.json()["id"]

    r = await client.delete(f"{PREFIX}/{id_}")
    assert r.status_code == 204

    r = await client.get(f"{PREFIX}/{id_}")
    assert r.status_code == 404


async def test_excluir_inexistente_retorna_404(client: AsyncClient) -> None:
    r = await client.delete(f"{PREFIX}/{uuid.uuid4()}")
    assert r.status_code == 404


async def test_excluir_em_uso_retorna_409(
    client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str
) -> None:
    r_carro = await client.post(PREFIX, json={"nome": "Carro Bloqueado"})
    carro_id = r_carro.json()["id"]

    await client.post(
        "/despesas",
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "200.00",
            "abastecimento": {"carro_id": carro_id, "quilometragem": 10000, "litros": "40.000"},
        },
    )

    r = await client.delete(f"{PREFIX}/{carro_id}")
    assert r.status_code == 409
