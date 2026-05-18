"""SEC filings, insider trading, and institutional ownership API endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.providers.sec_filings import get_insider_trades, get_institutional_holders, get_recent_filings

router = APIRouter(tags=['sec'])


@router.get('/filings/{symbol}')
async def recent_filings(
    symbol: str,
    count: int = Query(10, alias='count'),
) -> dict[str, Any]:
    """Get recent SEC filings (10-K, 10-Q, 8-K) for a symbol."""
    data = get_recent_filings(symbol.upper(), count=count)
    if 'error' in data:
        raise HTTPException(status_code=404, detail=data['error'])
    return data


@router.get('/insider/{symbol}')
async def insider_trades(
    symbol: str,
    count: int = Query(20, alias='count'),
) -> dict[str, Any]:
    """Get recent insider trading transactions (Form 4) for a symbol."""
    data = get_insider_trades(symbol.upper(), count=count)
    if 'error' in data:
        raise HTTPException(status_code=404, detail=data['error'])
    return data


@router.get('/institutional/{symbol}')
async def institutional_holders(
    symbol: str,
    count: int = Query(10, alias='count'),
) -> dict[str, Any]:
    """Get recent institutional holdings (13F) for a symbol."""
    data = get_institutional_holders(symbol.upper(), count=count)
    if 'error' in data:
        raise HTTPException(status_code=404, detail=data['error'])
    return data
