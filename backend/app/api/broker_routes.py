"""Broker sync API endpoint."""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.providers.alpaca import is_configured, sync_portfolio

router = APIRouter(prefix='/broker', tags=['broker'])


@router.get('/status')
async def get_broker_status() -> dict[str, Any]:
    """Check if Alpaca is configured."""
    return {
        'configured': is_configured(),
        'provider': 'alpaca',
    }


@router.post('/sync')
async def sync_from_broker() -> dict[str, Any]:
    """Sync portfolio positions from Alpaca."""
    if not is_configured():
        raise HTTPException(status_code=400, detail='Alpaca not configured')
    data = await sync_portfolio()
    if 'error' in data:
        raise HTTPException(status_code=401, detail=data['error'])
    return data
