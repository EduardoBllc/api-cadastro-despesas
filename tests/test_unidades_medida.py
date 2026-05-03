from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient

PREFIX = "/unidades-medida"


async def test_listar_retorna_lista(client: AsyncClient) -> None:
    r = await client.get(PREFIX)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_criar(client: AsyncClient) -> None:
    r = await client.post(PREFIX, json={"descricao": "Litro"})
    assert r.status_code == 201
    data = r.json()
    assert data["descricao"] == "Litro"
    assert "id" in data
    assert "data_cadastro" in data
    assert "data_alteracao" in data


async def test_criar_duplicado_retorna_409(client: AsyncClient) -> None:
    await client.post(PREFIX, json={"descricao": "Quilograma"})
    r = await client.post(PREFIX, json={"descricao": "Quilograma"})
    assert r.status_code == 409


async def test_criar_descricao_muito_longa_retorna_422(client: AsyncClient) -> None:
    r = await client.post(PREFIX, json={"descricao": "A" * 61})
    assert r.status_code == 422


async def test_obter(client: AsyncClient) -> None:
    r_criacao = await client.post(PREFIX, json={"descricao": "Metro"})
    id_ = r_criacao.json()["id"]

    r = await client.get(f"{PREFIX}/{id_}")
    assert r.status_code == 200
    assert r.json()["id"] == id_
    assert r.json()["descricao"] == "Metro"


async def test_obter_inexistente_retorna_404(client: AsyncClient) -> None:
    r = await client.get(f"{PREFIX}/{uuid.uuid4()}")
    assert r.status_code == 404


async def test_atualizar(client: AsyncClient) -> None:
    r_criacao = await client.post(PREFIX, json={"descricao": "Gramas"})
    id_ = r_criacao.json()["id"]

    r = await client.put(f"{PREFIX}/{id_}", json={"descricao": "Grama"})
    assert r.status_code == 200
    assert r.json()["id"] == id_
    assert r.json()["descricao"] == "Grama"


async def test_atualizar_inexistente_retorna_404(client: AsyncClient) -> None:
    r = await client.put(f"{PREFIX}/{uuid.uuid4()}", json={"descricao": "X"})
    assert r.status_code == 404


async def test_excluir(client: AsyncClient) -> None:
    r_criacao = await client.post(PREFIX, json={"descricao": "Para Excluir UM"})
    id_ = r_criacao.json()["id"]

    r = await client.delete(f"{PREFIX}/{id_}")
    assert r.status_code == 204

    r = await client.get(f"{PREFIX}/{id_}")
    assert r.status_code == 404


async def test_excluir_inexistente_retorna_404(client: AsyncClient) -> None:
    r = await client.delete(f"{PREFIX}/{uuid.uuid4()}")
    assert r.status_code == 404
