"""Fundamental data API endpoint."""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.providers.sec_edgar import FundamentalsProvider

router = APIRouter(prefix='/fundamentals', tags=['fundamentals'])

_provider = FundamentalsProvider()


@router.get('/{symbol}')
async def get_fundamentals(symbol: str) -> dict[str, Any]:
    """Fetch fundamental financial data for a symbol from SEC EDGAR."""
    data = _provider.get_fundamentals(symbol.upper())
    if 'error' in data:
        raise HTTPException(status_code=404, detail=data['error'])
    return data
