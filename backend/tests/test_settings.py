"""Tests for settings key-value endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_settings_returns_empty(client: AsyncClient):
    response = await client.get('/api/settings')
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.asyncio
async def test_put_and_get_setting(client: AsyncClient):
    response = await client.put('/api/settings', json={'key': 'theme', 'value': 'dark'})
    assert response.status_code == 200
    assert response.json() == {'key': 'theme', 'value': 'dark'}

    response = await client.get('/api/settings')
    assert response.json() == {'theme': 'dark'}


@pytest.mark.asyncio
async def test_get_setting_by_key(client: AsyncClient):
    await client.put('/api/settings', json={'key': 'language', 'value': 'en'})

    response = await client.get('/api/settings/language')
    assert response.status_code == 200
    assert response.json() == {'key': 'language', 'value': 'en'}


@pytest.mark.asyncio
async def test_get_setting_by_key_not_found(client: AsyncClient):
    response = await client.get('/api/settings/nonexistent')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_put_settings_empty_key_returns_422(client: AsyncClient):
    response = await client.put('/api/settings', json={'key': '', 'value': 'test'})
    assert response.status_code == 422
