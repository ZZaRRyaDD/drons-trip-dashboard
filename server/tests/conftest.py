# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import asyncio

import pytest
import pytest_asyncio
from alembic import command
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from yarl import URL

from app.__main__ import app
from app.config.utils import settings
from app.db.connection import get_session
from tests.utils import alembic_config_from_url, tmp_database

pytest_plugins = [
    "tests.fixtures.user",
]


@pytest.fixture()
def alembic_config(test_db_url):
    """
    Alembic configuration object, bound to temporary database.
    """
    return alembic_config_from_url(test_db_url.replace("+asyncpg", "+psycopg2"))

@pytest.fixture(scope="session")
def event_loop():
    """Один event loop на всю сессию тестов (иначе pytest-asyncio ругается)."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db_url():
    """Создаём временную БД для каждого теста и удаляем после."""
    db_url = URL(settings.database_uri)
    async with tmp_database(db_url) as url:
        yield str(url)


@pytest_asyncio.fixture
async def engine(test_db_url):
    engine = create_async_engine(test_db_url, future=True, echo=False)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """Создаём новую сессию на каждый тест."""
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def migrated_db(engine, test_db_url):
    """Прогоняем миграции Alembic перед тестами."""
    config = alembic_config_from_url(test_db_url.replace("+asyncpg", "+psycopg2"))

    command.upgrade(config, "head")
    yield
    # откатывать вниз до base не обязательно, tmp_database удалит


@pytest_asyncio.fixture
async def client(migrated_db, engine):
    """HTTP клиент, у которого get_db возвращает тестовую сессию."""

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
