"""DCF valuation API endpoint."""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.domain.dcf import calculate_dcf

router = APIRouter(prefix='/dcf', tags=['dcf'])


@router.get('/{symbol}')
async def dcf_valuation(symbol: str) -> dict[str, Any]:
    """Calculate DCF valuation for a symbol."""
    data = calculate_dcf(symbol.upper())
    if 'error' in data:
        raise HTTPException(status_code=404, detail=data['error'])
    return data
