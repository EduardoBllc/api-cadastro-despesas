# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install / sync dependencies (always use uv, not pip)
uv sync --extra dev

# Run dev server
uvicorn app.main:app --reload
# or
fastapi dev

# Run all tests (requires Docker for testcontainers)
pytest

# Run a single test file or test
pytest tests/test_status.py
pytest tests/test_status.py::test_status_db_connected

# Lint
ruff check app/ tests/ alembic/

# Format
ruff format app/ tests/ alembic/

# Lint + format in one pass (check only)
ruff check app/ tests/ alembic/ && ruff format --check app/ tests/ alembic/

# Apply all auto-fixes (including unsafe)
ruff check app/ tests/ alembic/ --fix --unsafe-fixes && ruff format app/ tests/ alembic/

# Migrations (Alembic) — reads DATABASE_URL from .env via app.config.Settings
alembic upgrade head                          # aplica todas as migrations pendentes
alembic downgrade -1                          # reverte a última migration
alembic revision --autogenerate -m "descricao" # gera nova migration a partir dos modelos
alembic current                               # exibe a revision atual do banco
alembic history                               # lista o histórico de migrations
```

## Architecture

### Request lifecycle
The app uses a **lifespan** context manager (`app/main.py`) to create a single `AsyncEngine` and `async_sessionmaker` on startup, storing both on `app.state`. Routers access them via `request.app.state`. There are no module-level singletons.

### Dependency injection pattern
Routers receive the engine/session factory through `request: Request` → `request.app.state.engine`. For new endpoints that need a DB session, use:
```python
from app.database import get_db_session

async def my_endpoint(request: Request):
    async with get_db_session(request.app.state.session_factory) as session:
        ...
```

### Adding a new router
1. Create `app/routers/<name>.py` with `router = APIRouter(prefix="/<name>", tags=["<name>"])`
2. Register in `app/main.py` → `app.include_router(<name>.router)`

### Database module (`app/database.py`)
- `build_engine(settings)` — production engine with connection pooling
- `build_session_factory(engine)` — sessionmaker with `expire_on_commit=False` (required for async)
- `get_db_session(session_factory)` — async context manager with auto commit/rollback
- `check_db_health(engine)` — raw connection query against `pg_stat_activity` / `pg_settings`

### Config (`app/config.py`)
`Settings` reads from `.env` via pydantic-settings. The `database_url` field uses `PostgresDsn` which must remain a **runtime import** (not under `TYPE_CHECKING`) because Pydantic evaluates field types at runtime — suppress the Ruff warning with `# noqa: TC002`.

### Testing
Tests spin up a real `postgres:17-alpine` container via testcontainers. The test engine uses `NullPool` (no connection pooling) to avoid event-loop mismatches between pytest function-scoped loops and session-scoped async fixtures.

The `client` fixture in `tests/conftest.py` bypasses the lifespan by injecting the test engine directly into `app.state`, so tests never connect to `localhost:5432`.

**All session-scoped async fixtures require `asyncio_default_fixture_loop_scope = "session"` in `pyproject.toml`** — without it, session-scoped async fixtures silently break.

### Models (`app/models/`)
- `base.py` — `Base` (DeclarativeBase) e `BaseModel` abstrato com `id` (UUID PK), `data_cadastro`, `data_alteracao`
- `data_alteracao` usa `onupdate=func.now()` — injetado automaticamente em updates via ORM
- Imports circulares entre modelos são resolvidos com `from __future__ import annotations` + imports reais sob `TYPE_CHECKING`
- Tipos usados em `Mapped[...]` (`uuid`, `date`, `Decimal`) devem permanecer como imports de runtime — SQLAlchemy usa `get_type_hints()` para inspecioná-los; suprimir avisos com `# noqa: TC003`
- `app/models/__init__.py` importa todos os modelos — **obrigatório** para registrá-los no `Base.metadata` antes de qualquer `create_all()` ou autogenerate do Alembic

### Migrations (Alembic)
- `alembic/env.py` lê a URL do banco via `get_settings()`, sem depender de `alembic.ini`
- O hook `post_write_hooks` em `alembic.ini` executa `ruff format` + `ruff check --fix` automaticamente em cada `alembic revision`
- `script.py.mako` já inclui `from __future__ import annotations` e sintaxe moderna de tipos

### Local dev database
```bash
docker compose up -d   # starts postgres:17-alpine on :5432
docker compose down    # stop (data persists)
docker compose down -v # stop + wipe data
```
Default credentials match `.env.example`: `postgres/postgres`, database `despesas`.
