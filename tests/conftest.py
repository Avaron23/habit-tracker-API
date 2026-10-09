import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.db import get_db
from app.main import app

TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@127.0.0.1:15433/habit_test_db"
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


@pytest.fixture
def registered_user(client, clean_database):
    user_data = {
        "username": "test-user",
        "password": "strong-password",
        "timezone": "Europe/Moscow",
    }
    r = client.post("/auth/register", json=user_data)
    return {**user_data, "id": r.json()["id"]}


@pytest.fixture
def login_response(client, registered_user):
    return client.post(
        "/auth/login",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )


@pytest.fixture
def refresh_cookie(login_response):
    return login_response.cookies["refresh_token"]


@pytest.fixture
def access_token(login_response):
    return login_response.json()["access_token"]   # ← из body


@pytest.fixture
def auth_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def second_user(client, clean_database):
    user_data = {
        "username": "test-user2",
        "password": "strong-password",
        "timezone": "Europe/Moscow",
    }
    reg_res = client.post("/auth/register", json=user_data)
    log_res = client.post(
        "/auth/login",
        data={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )
    user_data["headers"] = {"Authorization": f"Bearer {log_res.json()["access_token"]}"}
    habit_data = {
        "title": "some-title",
        "description": "some-description",
        "period": "daily"
    }
    hab_res = client.post("/habits", json=habit_data, headers=user_data["headers"])
    user_data["habit_id"] = hab_res.json()["id"] 
    return user_data