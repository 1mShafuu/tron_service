import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def client():
    with TestClient(app) as client:
        yield client
