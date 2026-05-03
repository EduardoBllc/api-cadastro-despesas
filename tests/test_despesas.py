from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient

PREFIX = "/despesas"


async def test_criar(client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str) -> None:
    r = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "150.00",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["estabelecimento_id"] == estabelecimento_id
    assert float(data["valor_total"]) == 150.0
    assert data["itens"] == []
    assert data["abastecimento"] is None
    assert "id" in data
    assert "data_cadastro" in data
    assert "data_alteracao" in data


async def test_criar_com_observacao(
    client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str
) -> None:
    r = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "80.00",
            "observacao": "Compra mensal",
        },
    )
    assert r.status_code == 201
    assert r.json()["observacao"] == "Compra mensal"


async def test_criar_sem_campos_obrigatorios_retorna_422(client: AsyncClient) -> None:
    r = await client.post(PREFIX, json={"valor_total": "50.00"})
    assert r.status_code == 422


async def test_criar_valor_total_negativo_retorna_422(
    client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str
) -> None:
    r = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "-10.00",
        },
    )
    assert r.status_code == 422


async def test_listar_retorna_estrutura_paginada(client: AsyncClient) -> None:
    r = await client.get(PREFIX)
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert data["total"] >= 0


async def test_listar_respeita_page_size(
    client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str
) -> None:
    for i in range(3):
        await client.post(
            PREFIX,
            json={
                "estabelecimento_id": estabelecimento_id,
                "categoria_despesa_id": categoria_despesa_id,
                "valor_total": "10.00",
            },
        )

    r = await client.get(f"{PREFIX}?page=1&page_size=1")
    assert r.status_code == 200
    data = r.json()
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert len(data["items"]) == 1
    assert data["total"] >= 3


async def test_obter_retorna_despesa_com_campo_itens(
    client: AsyncClient, despesa_fixture: dict
) -> None:
    id_ = despesa_fixture["id"]
    r = await client.get(f"{PREFIX}/{id_}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == id_
    assert data["estabelecimento_id"] == despesa_fixture["estabelecimento_id"]
    assert "itens" in data
    assert isinstance(data["itens"], list)


async def test_obter_inexistente_retorna_404(client: AsyncClient) -> None:
    r = await client.get(f"{PREFIX}/{uuid.uuid4()}")
    assert r.status_code == 404


async def test_atualizar(client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str) -> None:
    r_criacao = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "50.00",
        },
    )
    id_ = r_criacao.json()["id"]

    r = await client.put(
        f"{PREFIX}/{id_}", json={"estabelecimento_id": estabelecimento_id, "valor_total": "75.00"}
    )
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == id_
    assert data["estabelecimento_id"] == estabelecimento_id
    assert float(data["valor_total"]) == 75.0
    assert "itens" in data


async def test_atualizar_campo_parcial(
    client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str
) -> None:
    r_criacao = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "200.00",
        },
    )
    id_ = r_criacao.json()["id"]

    r = await client.put(f"{PREFIX}/{id_}", json={"observacao": "Nota fiscal anexada"})
    assert r.status_code == 200
    data = r.json()
    assert data["estabelecimento_id"] == estabelecimento_id
    assert data["observacao"] == "Nota fiscal anexada"


async def test_atualizar_inexistente_retorna_404(client: AsyncClient) -> None:
    r = await client.put(f"{PREFIX}/{uuid.uuid4()}", json={"estabelecimento_id": str(uuid.uuid4())})
    assert r.status_code == 404


async def test_excluir(client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str) -> None:
    r_criacao = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "30.00",
        },
    )
    id_ = r_criacao.json()["id"]

    r = await client.delete(f"{PREFIX}/{id_}")
    assert r.status_code == 204

    r = await client.get(f"{PREFIX}/{id_}")
    assert r.status_code == 404


async def test_excluir_inexistente_retorna_404(client: AsyncClient) -> None:
    r = await client.delete(f"{PREFIX}/{uuid.uuid4()}")
    assert r.status_code == 404


# ── Itens embutidos na criação ──────────────────────────────────────────────


async def test_criar_com_itens_embutidos(
    client: AsyncClient,
    categoria_despesa_id: str,
    item_id: str,
    estabelecimento_id: str,
) -> None:
    r = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "100.00",
            "itens": [
                {
                    "item_id": item_id,
                    "quantidade": "2",
                    "valor_unitario": "50.00",
                }
            ],
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert len(data["itens"]) == 1
    assert data["itens"][0]["item_id"] == item_id


async def test_criar_com_item_categoria_invalida_retorna_400(
    client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str
) -> None:
    r = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "50.00",
            "itens": [
                {
                    "item_id": str(uuid.uuid4()),
                    "quantidade": "1",
                    "valor_unitario": "50.00",
                }
            ],
        },
    )
    assert r.status_code == 400


# ── Abastecimento sub-resource ──────────────────────────────────────────────


async def test_criar_com_abastecimento_embutido(
    client: AsyncClient,
    categoria_despesa_id: str,
    carro_fixture: dict,
    estabelecimento_id: str,
) -> None:
    r = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "200.00",
            "abastecimento": {
                "carro_id": carro_fixture["id"],
                "quilometragem": 55000,
                "litros": "40.000",
            },
        },
    )
    assert r.status_code == 201
    data = r.json()
    ab = data["abastecimento"]
    assert ab is not None
    assert ab["carro_id"] == carro_fixture["id"]
    assert ab["quilometragem"] == 55000
    assert float(ab["valor_total"]) == 200.0
    assert float(ab["valor_por_litro"]) == 5.0
    assert ab["despesa_id"] == data["id"]


async def test_criar_com_abastecimento_carro_invalido_retorna_404(
    client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str
) -> None:
    r = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "100.00",
            "abastecimento": {
                "carro_id": str(uuid.uuid4()),
                "quilometragem": 10000,
                "litros": "30.000",
            },
        },
    )
    assert r.status_code == 404


async def test_obter_retorna_abastecimento_nulo_sem_combustivel(
    client: AsyncClient, despesa_fixture: dict
) -> None:
    r = await client.get(f"{PREFIX}/{despesa_fixture['id']}")
    assert r.status_code == 200
    assert r.json()["abastecimento"] is None


async def test_adicionar_abastecimento(
    client: AsyncClient, categoria_despesa_id: str, carro_fixture: dict, estabelecimento_id: str
) -> None:
    r_despesa = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "150.00",
        },
    )
    despesa_id = r_despesa.json()["id"]

    r = await client.post(
        f"{PREFIX}/{despesa_id}/abastecimento",
        json={"carro_id": carro_fixture["id"], "quilometragem": 70000, "litros": "30.000"},
    )
    assert r.status_code == 201
    ab = r.json()
    assert ab["despesa_id"] == despesa_id
    assert float(ab["valor_total"]) == 150.0
    assert float(ab["valor_por_litro"]) == 5.0


async def test_adicionar_abastecimento_ja_existe_retorna_409(
    client: AsyncClient,
    categoria_despesa_id: str,
    carro_fixture: dict,
    estabelecimento_id: str,
) -> None:
    r_despesa = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "100.00",
            "abastecimento": {
                "carro_id": carro_fixture["id"],
                "quilometragem": 80000,
                "litros": "20.000",
            },
        },
    )
    despesa_id = r_despesa.json()["id"]

    r = await client.post(
        f"{PREFIX}/{despesa_id}/abastecimento",
        json={"carro_id": carro_fixture["id"], "quilometragem": 80001, "litros": "20.000"},
    )
    assert r.status_code == 409


async def test_adicionar_abastecimento_despesa_inexistente_retorna_404(
    client: AsyncClient, carro_fixture: dict
) -> None:
    r = await client.post(
        f"{PREFIX}/{uuid.uuid4()}/abastecimento",
        json={"carro_id": carro_fixture["id"], "quilometragem": 10000, "litros": "30.000"},
    )
    assert r.status_code == 404


async def test_atualizar_abastecimento(
    client: AsyncClient, categoria_despesa_id: str, carro_fixture: dict, estabelecimento_id: str
) -> None:
    r_despesa = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "200.00",
            "abastecimento": {
                "carro_id": carro_fixture["id"],
                "quilometragem": 90000,
                "litros": "40.000",
            },
        },
    )
    despesa_id = r_despesa.json()["id"]

    r = await client.put(
        f"{PREFIX}/{despesa_id}/abastecimento", json={"litros": "50.000"}
    )
    assert r.status_code == 200
    ab = r.json()
    assert float(ab["litros"]) == 50.0
    assert float(ab["valor_por_litro"]) == 4.0  # 200 / 50


async def test_atualizar_abastecimento_inexistente_retorna_404(
    client: AsyncClient, despesa_fixture: dict, carro_fixture: dict
) -> None:
    r = await client.put(
        f"{PREFIX}/{despesa_fixture['id']}/abastecimento",
        json={"quilometragem": 99999},
    )
    assert r.status_code == 404


async def test_excluir_abastecimento(
    client: AsyncClient, categoria_despesa_id: str, carro_fixture: dict, estabelecimento_id: str
) -> None:
    r_despesa = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "100.00",
            "abastecimento": {
                "carro_id": carro_fixture["id"],
                "quilometragem": 95000,
                "litros": "20.000",
            },
        },
    )
    despesa_id = r_despesa.json()["id"]

    r = await client.delete(f"{PREFIX}/{despesa_id}/abastecimento")
    assert r.status_code == 204

    r = await client.get(f"{PREFIX}/{despesa_id}")
    assert r.json()["abastecimento"] is None


async def test_excluir_despesa_remove_abastecimento(
    client: AsyncClient, categoria_despesa_id: str, carro_fixture: dict, estabelecimento_id: str
) -> None:
    r_despesa = await client.post(
        PREFIX,
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "100.00",
            "abastecimento": {
                "carro_id": carro_fixture["id"],
                "quilometragem": 99000,
                "litros": "20.000",
            },
        },
    )
    despesa_id = r_despesa.json()["id"]
    ab_id = r_despesa.json()["abastecimento"]["id"]

    await client.delete(f"{PREFIX}/{despesa_id}")

    r = await client.get(f"/abastecimentos?carro_id={carro_fixture['id']}")
    ids = [item["id"] for item in r.json()["items"]]
    assert ab_id not in ids
    despesa_id = r_despesa.json()["id"]
    ab_id = r_despesa.json()["abastecimento"]["id"]

    await client.delete(f"{PREFIX}/{despesa_id}")

    r = await client.get(f"/abastecimentos?carro_id={carro_fixture['id']}")
    ids = [item["id"] for item in r.json()["items"]]
    assert ab_id not in ids
