import asyncio
from pathlib import Path

from alembic.config import Config as AlembicConfig
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from fastapi import APIRouter, HTTPException, Request

from alembic import command

router = APIRouter(prefix="/migrations", tags=["migrations"])

ALEMBIC_INI = Path(__file__).parent.parent.parent / "alembic.ini"


def _alembic_config() -> AlembicConfig:
    return AlembicConfig(str(ALEMBIC_INI))


async def _get_current_revision(request: Request) -> str | None:
    async with request.app.state.engine.connect() as conn:

        def _read(sync_conn) -> str | None:
            return MigrationContext.configure(sync_conn).get_current_revision()

        return await conn.run_sync(_read)


@router.get("")
async def list_migrations(request: Request) -> dict:
    """Dry-run: retorna as migrations pendentes sem aplicá-las."""
    current_rev = await _get_current_revision(request)

    script = ScriptDirectory.from_config(_alembic_config())
    pending = list(reversed(list(script.iterate_revisions("head", current_rev or "base"))))

    return {
        "current_revision": current_rev,
        "up_to_date": len(pending) == 0,
        "pending": [{"revision": r.revision, "description": r.doc} for r in pending],
    }


@router.post("")
async def run_migrations(request: Request) -> dict:
    """Aplica todas as migrations pendentes."""
    revision_before = await _get_current_revision(request)

    def _upgrade() -> None:
        command.upgrade(_alembic_config(), "head")

    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _upgrade)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    revision_after = await _get_current_revision(request)

    return {
        "previous_revision": revision_before,
        "current_revision": revision_after,
        "changed": revision_before != revision_after,
    }
