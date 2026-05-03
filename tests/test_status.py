from httpx import AsyncClient


async def test_status_api_ok(client: AsyncClient) -> None:
    response = await client.get("/status")
    assert response.status_code == 200
    assert response.json()["api"] == "ok"


async def test_status_db_connected(client: AsyncClient) -> None:
    response = await client.get("/status")
    assert response.json()["database"]["status"] == "ok"


async def test_status_db_connections(client: AsyncClient) -> None:
    response = await client.get("/status")
    db = response.json()["database"]
    assert isinstance(db["active_connections"], int)
    assert isinstance(db["max_connections"], int)
    assert db["max_connections"] > 0
