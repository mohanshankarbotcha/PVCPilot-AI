import asyncio
import pytest
import pytest_asyncio
from unittest.mock import patch
from mongomock_motor import AsyncMongoMockClient

# Create a global mock client instance
mock_mongo_client = AsyncMongoMockClient()

# Patch AsyncIOMotorClient in app.database before imports
with patch("app.database.AsyncIOMotorClient", return_value=mock_mongo_client):
    from app.main import app
    from app.database import init_db
    from app.seed.test_seed import seed_test_data

from httpx import AsyncClient, ASGITransport

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_db():
    """Initialize test database with minimal seed data using mock client"""
    # Initialize beanie using our mocked client inside init_db
    with patch("app.database.AsyncIOMotorClient", return_value=mock_mongo_client):
        await init_db()
    await seed_test_data()
    yield
    # No close_db needed for mongomock-motor in memory database

@pytest_asyncio.fixture
async def client(test_db):
    """Async HTTP client for FastAPI app"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def auth_headers_owner(client):
    """Returns auth headers for Factory Owner role"""
    resp = await client.post("/api/auth/login", json={
        "email": "owner@pvcpilot.com",
        "password": "PVCPilot@2025"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def auth_headers_operator(client):
    """Returns auth headers for Operator (lowest permission) role"""
    resp = await client.post("/api/auth/login", json={
        "email": "operator@pvcpilot.com",
        "password": "PVCPilot@2025"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def auth_headers_quality(client):
    resp = await client.post("/api/auth/login", json={
        "email": "quality@pvcpilot.com",
        "password": "PVCPilot@2025"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
