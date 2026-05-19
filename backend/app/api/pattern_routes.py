"""Chart pattern detection API endpoint."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import PriceHistory, WatchlistEntry
from app.domain.patterns import detect_patterns

router = APIRouter(prefix='/technicals', tags=['technicals'])


@router.post('/{symbol}/patterns')
async def get_patterns(
    symbol: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Detect chart patterns in price history."""
    sym = symbol.upper()

    # Check watchlist
    result = await session.execute(
        select(WatchlistEntry).where(WatchlistEntry.symbol == sym)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f'{sym} not in watchlist')

    # Get price history
    price_result = await session.execute(
        select(PriceHistory)
        .where(PriceHistory.symbol == sym)
        .order_by(PriceHistory.date)
    )
    rows = price_result.scalars().all()

    if not rows:
        return {'symbol': sym, 'patterns': []}

    prices = [
        {
            'high': r.high_price,
            'low': r.low_price,
            'close': r.close_price,
            'open': r.open_price,
            'volume': r.volume,
            'date': str(r.date),
        }
        for r in rows
    ]

    patterns = detect_patterns(prices)

    return {'symbol': sym, 'patterns': patterns}
