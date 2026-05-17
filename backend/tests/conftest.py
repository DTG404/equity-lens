"""Test fixtures for async DB testing."""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.domain.db_models import Base

TEST_DB_URL = 'sqlite+aiosqlite://'


@pytest.fixture(scope='session')
def _engine() -> Any:
    engine = create_async_engine(TEST_DB_URL, echo=False)
    return engine


@pytest_asyncio.fixture(autouse=True)
async def _create_tables(_engine: Any) -> AsyncGenerator[None, None]:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_db_session(_engine: Any) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def override_get_session(_engine: Any) -> AsyncGenerator[None, None]:
    """Override the app's get_session dependency to use the test DB."""
    from app.core.db import get_session
    from app.main import app

    factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)

    async def _test_session() -> AsyncGenerator[AsyncSession, None]:
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_session] = _test_session
    yield
    app.dependency_overrides.clear()
