"""Finnhub news and earnings API endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.providers.finnhub import fetch_earnings, fetch_earnings_calendar, fetch_news

router = APIRouter(prefix='/finnhub', tags=['finnhub'])


@router.get('/news/{symbol}')
async def company_news(symbol: str) -> dict[str, Any]:
    """Get recent news for a symbol from Finnhub."""
    data = await fetch_news(symbol.upper())
    if 'error' in data:
        raise HTTPException(status_code=404, detail=data['error'])
    return data


@router.get('/earnings/{symbol}')
async def company_earnings(symbol: str) -> dict[str, Any]:
    """Get earnings data for a symbol from Finnhub."""
    data = await fetch_earnings(symbol.upper())
    if 'error' in data:
        raise HTTPException(status_code=404, detail=data['error'])
    return data


@router.get('/earnings-calendar')
async def earnings_calendar() -> list[dict[str, Any]]:
    """Get upcoming earnings across the market."""
    return await fetch_earnings_calendar()
