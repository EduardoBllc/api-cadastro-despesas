# API Cadastro de Despesas

A modern, asynchronous FastAPI application for managing expenses, items, car maintenance (refueling), and categories.

## Project Overview

- **Purpose**: Backend API for expense tracking and vehicle maintenance management.
- **Main Technologies**: 
    - **Framework**: FastAPI (Asynchronous)
    - **Database**: PostgreSQL with SQLAlchemy 2.0 (Async)
    - **Migrations**: Alembic
    - **Validation**: Pydantic v2
    - **Package Management**: `uv`
    - **Testing**: Pytest with `testcontainers` (Postgres)
    - **Linting/Formatting**: Ruff

## Architecture & Request Lifecycle

- **Lifespan Context**: The application uses a `lifespan` manager in `app/main.py` to handle the `AsyncEngine` and `async_sessionmaker`. These are stored in `app.state` to avoid module-level singletons.
- **Dependency Injection**: Routers access the database engine via `request.app.state`. Sessions should be managed using the `app.database.get_db_session` context manager.
- **Models**: Located in `app/models/`. Uses a custom `BaseModel` (in `base.py`) providing UUID primary keys, `data_cadastro`, and `data_alteracao` (with `onupdate`).
- **Services**: Business logic is encapsulated in `app/services/`.
- **Schemas**: Pydantic models for request/response validation in `app/schemas/`.

## Key Commands

### Development

```bash
# Install dependencies
uv sync --extra dev

# Run development server
fastapi dev # or uvicorn app.main:app --reload

# Database (Docker Compose)
docker compose up -d   # Start local Postgres
docker compose down    # Stop
```

### Testing & Quality

```bash
# Run all tests (requires Docker for testcontainers)
pytest

# Lint and format
ruff check . --fix
ruff format .
```

### Migrations (Alembic)

```bash
# Apply migrations
alembic upgrade head

# Generate new migration
alembic revision --autogenerate -m "description"

# Rollback
alembic downgrade -1
```

## Development Conventions

- **Tooling**: Always use `uv` for dependency management.
- **Typing**: Use `from __future__ import annotations` and modern Python 3.13 type hints.
- **SQLAlchemy Types**: Keep `uuid`, `date`, and `Decimal` as runtime imports (not `TYPE_CHECKING`) in models, as SQLAlchemy inspects them via `get_type_hints()`. Use `# noqa: TC003` to suppress Ruff warnings.
- **Pydantic Settings**: `PostgresDsn` must be a runtime import in `app/config.py` (`# noqa: TC002`).
- **Model Registration**: All models must be imported in `app/models/__init__.py` for Alembic autogenerate to work correctly.
- **Naming**: Brazilian Portuguese for domain entities (e.g., `despesa`, `abastecimento`, `carro`).

## Testing Strategy

- **Integration Tests**: Tests use `testcontainers` to spin up a real PostgreSQL instance.
- **Configuration**: The `client` fixture in `tests/conftest.py` overrides `app.state.engine` with a test-specific engine using `NullPool`.
- **Async Fixtures**: Session-scoped async fixtures require `asyncio_default_fixture_loop_scope = "session"` in `pyproject.toml`.
