from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import Request  # noqa: TC002
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from app.config import Settings


def build_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        str(settings.database_url),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_pre_ping=True,
        echo=False,
    )


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db(request: Request) -> AsyncGenerator[AsyncSession]:
    """Dependency for inject database session into routes."""
    session_factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_db_health(engine: AsyncEngine) -> dict:
    try:
        async with engine.connect() as conn:
            active = await conn.execute(
                text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            )
            max_conn = await conn.execute(
                text("SELECT setting FROM pg_settings WHERE name = 'max_connections'")
            )
            return {
                "status": "ok",
                "active_connections": active.scalar_one(),
                "max_connections": int(max_conn.scalar_one()),
            }
    except Exception as exc:
        return {
            "status": "fail",
            "detail": str(exc),
            "active_connections": None,
            "max_connections": None,
        }
