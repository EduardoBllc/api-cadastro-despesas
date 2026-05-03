from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from app.config import Settings
from app.database import build_session_factory
from app.main import create_app
from app.models import Base

POSTGRES_IMAGE = "postgres:17-alpine"


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer(POSTGRES_IMAGE, driver="asyncpg") as container:
        yield container


@pytest.fixture(scope="session")
def test_settings(postgres_container: PostgresContainer) -> Settings:
    return Settings(database_url=postgres_container.get_connection_url())


@pytest_asyncio.fixture(scope="session")
async def db_engine(test_settings: Settings) -> AsyncGenerator[AsyncEngine]:
    # NullPool avoids event-loop mismatch issues between tests: each connect()
    # creates a fresh connection and closes it immediately on exit.
    engine = create_async_engine(str(test_settings.database_url), poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def client(test_settings: Settings, db_engine: AsyncEngine) -> AsyncGenerator[AsyncClient]:
    fastapi_app = create_app()
    fastapi_app.state.engine = db_engine
    fastapi_app.state.session_factory = build_session_factory(db_engine)
    fastapi_app.state.settings = test_settings

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def categoria_despesa_id(client: AsyncClient) -> str:
    r = await client.post("/categorias-despesa", json={"descricao": "Fixture CategoriaDespesa"})
    assert r.status_code == 201
    return r.json()["id"]


@pytest_asyncio.fixture(scope="session")
async def categoria_item_id(client: AsyncClient) -> str:
    r = await client.post("/categorias-item", json={"descricao": "Fixture CategoriaItem"})
    assert r.status_code == 201
    return r.json()["id"]

@pytest_asyncio.fixture(scope="session")
async def item_id(client: AsyncClient, categoria_item_id: str, unidade_medida_id: str) -> str:
    r = await client.post(
        "/itens",
        json={
            "descricao": "Fixture Item",
            "categoria_item_id": categoria_item_id,
            "unidade_medida_id": unidade_medida_id,
        },
    )
    assert r.status_code == 201
    return r.json()["id"]


@pytest_asyncio.fixture(scope="session")
async def unidade_medida_id(client: AsyncClient) -> str:
    r = await client.post("/unidades-medida", json={"descricao": "Fixture Unidade"})
    assert r.status_code == 201
    return r.json()["id"]


@pytest_asyncio.fixture(scope="session")
async def tipo_estabelecimento_id(client: AsyncClient) -> str:
    r = await client.post("/tipos-estabelecimento", json={"descricao": "Fixture TipoEstabelecimento"})
    assert r.status_code == 201
    return r.json()["id"]


@pytest_asyncio.fixture(scope="session")
async def estabelecimento_id(client: AsyncClient, tipo_estabelecimento_id: str) -> str:
    r = await client.post("/estabelecimentos", json={"descricao": "Fixture Estabelecimento", "tipo_id": tipo_estabelecimento_id})
    assert r.status_code == 201
    return r.json()["id"]


@pytest_asyncio.fixture(scope="session")
async def despesa_fixture(client: AsyncClient, categoria_despesa_id: str, estabelecimento_id: str) -> dict:
    r = await client.post(
        "/despesas",
        json={
            "estabelecimento_id": estabelecimento_id,
            "categoria_despesa_id": categoria_despesa_id,
            "valor_total": "250.00",
        },
    )
    assert r.status_code == 201
    return r.json()


@pytest_asyncio.fixture(scope="session")
async def carro_fixture(client: AsyncClient) -> dict:
    r = await client.post("/carros", json={"nome": "Carro Fixture", "placa": "TST0001"})
    assert r.status_code == 201
    return r.json()
