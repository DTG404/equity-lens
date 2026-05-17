"""Database engine, session factory, and FastAPI dependency."""

import os
from collections.abc import AsyncGenerator
from typing import Any

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings as app_settings

_engine: Any = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_db_url() -> str:
    """Return the database URL, converting common schemes for async access."""
    url = app_settings.database_url
    if url.startswith('sqlite:///'):
        return url.replace('sqlite:///', 'sqlite+aiosqlite:///', 1)
    if url.startswith('postgresql://'):
        return url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    if url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql+asyncpg://', 1)
    return url


def get_sync_db_url() -> str:
    """Convert the async DB URL to a synchronous one for Alembic."""
    url = get_db_url()
    if url.startswith('sqlite+aiosqlite:///'):
        return url.replace('sqlite+aiosqlite:///', 'sqlite:///', 1)
    if url.startswith('postgresql+asyncpg://'):
        return url.replace('postgresql+asyncpg://', 'postgresql+psycopg2://', 1)
    return url


async def init_db() -> None:
    """Create engine and run Alembic migrations."""
    global _engine, _async_session_factory
    url = get_db_url()
    _engine = create_async_engine(url, echo=False)
    _async_session_factory = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )

    _alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '../../alembic.ini'))
    _alembic_cfg.set_main_option('sqlalchemy.url', get_sync_db_url())
    alembic_upgrade(_alembic_cfg, 'head')


async def close_db() -> None:
    """Dispose the engine."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a session."""
    if _async_session_factory is None:
        await init_db()
    assert _async_session_factory is not None
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
