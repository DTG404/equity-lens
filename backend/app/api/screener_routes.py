"""Stock screener API endpoint."""

from typing import Any

from fastapi import APIRouter, Query

from app.providers.screener import screen_stocks

router = APIRouter(prefix='/screener', tags=['screener'])


@router.get('')
async def get_screener(
    price_min: float | None = Query(None, alias='priceMin'),
    price_max: float | None = Query(None, alias='priceMax'),
    sector: str | None = None,
    rsi_min: float | None = Query(None, alias='rsiMin'),
    rsi_max: float | None = Query(None, alias='rsiMax'),
    volume_min: int | None = Query(None, alias='volumeMin'),
    sort_by: str = Query('symbol', alias='sortBy'),
    sort_dir: str = Query('asc', alias='sortDir'),
    limit: int = 50,
    skip: int = 0,
) -> dict[str, Any]:
    """Screen the stock universe by price, sector, RSI, and volume."""
    return await screen_stocks(
        price_min=price_min,
        price_max=price_max,
        sector=sector,
        rsi_min=rsi_min,
        rsi_max=rsi_max,
        volume_min=volume_min,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
        skip=skip,
    )
