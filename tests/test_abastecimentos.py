from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient

PREFIX = "/abastecimentos"


def _ab_payload(carro_id: str, km: int = 50000, litros: str = "40.000") -> dict:
    return {"carro_id": carro_id, "quilometragem": km, "litros": litros}


async def _criar_despesa_com_ab(
    client: AsyncClient,
    carro_id: str,
    categoria_despesa_id: str,
    estabelecimento_id: str,
    km: int = 50000,
    litros: str = "40.000",
    valor_total: str = "200.00",
) -> dict:
    r = await client.post(
        "/despesas",
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": valor_total,
            "abastecimento": _ab_payload(carro_id, km, litros),
        },
    )
    assert r.status_code == 201
    return r.json()


async def test_listar_retorna_estrutura_paginada(client: AsyncClient) -> None:
    r = await client.get(PREFIX)
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "items" in data
    assert isinstance(data["items"], list)


async def test_listar_filtra_por_carro_id(
    client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str
) -> None:
    r_carro = await client.post("/carros", json={"nome": "Carro Filtro AB"})
    carro_id = r_carro.json()["id"]

    await _criar_despesa_com_ab(client, carro_id, categoria_despesa_id, estabelecimento_id, km=1000)
    await _criar_despesa_com_ab(client, carro_id, categoria_despesa_id, estabelecimento_id, km=2000)

    r = await client.get(f"{PREFIX}?carro_id={carro_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert all(item["carro_id"] == carro_id for item in data["items"])


async def test_listar_item_contem_valor_total_e_valor_por_litro(
    client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str
) -> None:
    r_carro = await client.post("/carros", json={"nome": "Carro VPL"})
    carro_id = r_carro.json()["id"]
    await _criar_despesa_com_ab(
        client,
        carro_id,
        categoria_despesa_id,
        estabelecimento_id,
        km=5000,
        litros="40.000",
        valor_total="200.00",
    )

    r = await client.get(f"{PREFIX}?carro_id={carro_id}")
    item = r.json()["items"][0]
    assert float(item["valor_total"]) == 200.0
    assert float(item["valor_por_litro"]) == 5.0


async def test_km_rodados_nulo_no_primeiro_abastecimento(
    client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str
) -> None:
    r_carro = await client.post("/carros", json={"nome": "Carro Km Nulo AB"})
    carro_id = r_carro.json()["id"]

    despesa = await _criar_despesa_com_ab(
        client, carro_id, categoria_despesa_id, estabelecimento_id, km=10000
    )
    ab = despesa["abastecimento"]
    assert ab["km_rodados"] is None
    assert ab["km_por_litro"] is None


async def test_km_rodados_calculado_no_segundo_abastecimento(
    client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str
) -> None:
    r_carro = await client.post("/carros", json={"nome": "Carro Km Calc AB"})
    carro_id = r_carro.json()["id"]

    await _criar_despesa_com_ab(client, carro_id, categoria_despesa_id, estabelecimento_id, km=50000)
    despesa2 = await _criar_despesa_com_ab(
        client,
        carro_id,
        categoria_despesa_id,
        estabelecimento_id,
        km=50500,
        litros="50.000",
        valor_total="300.00",
    )

    ab = despesa2["abastecimento"]
    assert ab["km_rodados"] == 500
    assert float(ab["km_por_litro"]) == 10.0
