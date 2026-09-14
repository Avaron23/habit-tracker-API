import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.db import get_db
from app.main import app


TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres"
    "@127.0.0.1:15433/habit_test_db"
)

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
)


async def truncate_test_tables():
    async with test_engine.begin() as connection:
        await connection.execute(
            text(
                """
                TRUNCATE TABLE
                    habit_logs,
                    refresh_tokens,
                    habits,
                    users
                RESTART IDENTITY CASCADE
                """
            )
        )


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def clean_database(anyio_backend):
    await truncate_test_tables()

    yield

    await truncate_test_tables()


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def db_session(
    clean_database,
    anyio_backend,
):
    async with TestSessionLocal() as session:
        yield session