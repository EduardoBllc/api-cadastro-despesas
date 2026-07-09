from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from app.config import get_settings
from app.database import build_engine, build_session_factory
from app.errors import setup_exception_handlers
from app.logging_conf import setup_logging
from app.routers import (
    abastecimentos,
    carros,
    categorias_despesa,
    categorias_item,
    configuracoes,
    despesas,
    estabelecimentos,
    itens,
    itens_despesa,
    migrations,
    relatorios,
    status,
    sugestoes,
    tipos_estabelecimento,
    unidades_medida,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = get_settings()
    engine = build_engine(settings)
    app.state.engine = engine
    app.state.session_factory = build_session_factory(engine)
    app.state.settings = settings
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="API Cadastro de Despesas", version="0.1.0", lifespan=lifespan)
    app.include_router(status.router)
    app.include_router(migrations.router)
    app.include_router(categorias_despesa.router)
    app.include_router(categorias_item.router)
    app.include_router(unidades_medida.router)
    app.include_router(itens.router)
    app.include_router(configuracoes.router)
    app.include_router(tipos_estabelecimento.router)
    app.include_router(estabelecimentos.router)
    app.include_router(sugestoes.router)
    app.include_router(despesas.router)
    app.include_router(itens_despesa.router)
    app.include_router(carros.router)
    app.include_router(abastecimentos.router)
    app.include_router(relatorios.router)

    setup_exception_handlers(app)

    return app


app = create_app()
