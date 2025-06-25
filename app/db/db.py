from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from app.core.config import settings


class AsyncPostgresPool:
    _pool: Optional[AsyncConnectionPool] = None

    @classmethod
    async def initialize(cls, dsn, min_size, max_size) -> None:
        if cls._pool is None:
            cls._pool = AsyncConnectionPool(
                conninfo=settings.SQLALCHEMY_DATABASE_URI,
                max_size=10,
                kwargs={
                    "autocommit": True,
                    "prepare_threshold": 0,
                    "row_factory": dict_row,
                },
            )

    @classmethod
    def is_initialized(cls) -> bool:
        return cls._pool is not None

    @classmethod
    async def get_pool(cls) -> AsyncConnectionPool:
        if cls._pool is None:
            raise RuntimeError(
                "PostgresPool is not initialized. Call initialize() first."
            )
        return cls._pool

    @classmethod
    @asynccontextmanager
    async def connection(cls) -> AsyncGenerator:
        if cls._pool is None:
            raise RuntimeError(
                "PostgresPool is not initialized. Call initialize() first."
            )
        async with cls._pool.connection() as conn:
            yield conn

    @classmethod
    async def close_pool(cls) -> None:
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None
