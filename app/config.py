from functools import lru_cache

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: PostgresDsn = "postgresql+asyncpg://postgres:postgres@localhost:5432/despesas"
    db_pool_size: int = 10
    db_max_overflow: int = 5
    db_pool_timeout: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
