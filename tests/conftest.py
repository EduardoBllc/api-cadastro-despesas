import random
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pathlib import Path

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
from app.services import nfce as nfce_service
from app.services.nfce_parser import TAMANHO_CHAVE, TAMANHO_CNPJ

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


FIXTURE_NFCE = Path(__file__).parent / "fixtures" / "nfce_rs.html"
CNPJ_FIXTURE_FORMATADO = "01.132.478/0023-43"
CHAVE_FIXTURE_FORMATADA = "4326 0801 1324 7800 2343 6510 8000 3191 5211 6495 4990"
UF_RS = "43"
TAMANHO_GRUPO_CHAVE = 4
HASH_FICTICIO = "A" * 40


@dataclass(frozen=True)
class NotaTeste:
    html: str
    cnpj: str
    chave: str
    url: str


def formatar_cnpj(cnpj: str) -> str:
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def _digitos_aleatorios(quantidade: int) -> str:
    return f"{random.randrange(10**quantidade):0{quantidade}d}"


@pytest.fixture
def gerar_nota():
    """HTML da nota de exemplo com CNPJ/chave trocados — isola os testes que compartilham o banco."""
    base = FIXTURE_NFCE.read_text(encoding="utf-8")

    def _gerar(cnpj: str | None = None) -> NotaTeste:
        cnpj = cnpj or _digitos_aleatorios(TAMANHO_CNPJ)
        chave = UF_RS + _digitos_aleatorios(TAMANHO_CHAVE - len(UF_RS))
        chave_formatada = " ".join(
            chave[i : i + TAMANHO_GRUPO_CHAVE]
            for i in range(0, TAMANHO_CHAVE, TAMANHO_GRUPO_CHAVE)
        )
        html = base.replace(CNPJ_FIXTURE_FORMATADO, formatar_cnpj(cnpj)).replace(
            CHAVE_FIXTURE_FORMATADA, chave_formatada
        )
        url = f"https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p={chave}|2|1|2|{HASH_FICTICIO}"
        return NotaTeste(html=html, cnpj=cnpj, chave=chave, url=url)

    return _gerar


@pytest.fixture
def sefaz(monkeypatch: pytest.MonkeyPatch):
    """Substitui a busca na SEFAZ: a próxima importação recebe o HTML informado."""

    def _responder(html: str) -> None:
        async def _buscar(p: str) -> str:
            return html

        monkeypatch.setattr(nfce_service, "buscar_html", _buscar)

    return _responder
