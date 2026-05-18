"""Technical indicators API endpoint."""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.domain.technicals import compute_technicals

router = APIRouter(prefix='/technicals', tags=['technicals'])


@router.get('/{symbol}')
async def get_technicals(symbol: str) -> dict[str, Any]:
    """Compute and return technical indicators for a symbol."""
    data = await compute_technicals(symbol.upper())
    if 'error' in data:
        raise HTTPException(status_code=404, detail=data['error'])
    return data
