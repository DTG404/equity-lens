"""Social sentiment API endpoint."""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.providers.social_sentiment import get_sentiment

router = APIRouter(prefix='/sentiment', tags=['sentiment'])


@router.get('/{symbol}')
async def social_sentiment(symbol: str) -> dict[str, Any]:
    """Get social sentiment for a symbol from StockTwits."""
    data = get_sentiment(symbol.upper())
    if 'error' in data:
        raise HTTPException(status_code=404, detail=data['error'])
    return data
