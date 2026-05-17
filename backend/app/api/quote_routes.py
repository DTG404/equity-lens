"""Quote and price history endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import PriceSnapshot, WatchlistEntry
from app.domain.models import TickerSymbol
from app.providers.mock_market import MockMarketDataProvider

router = APIRouter(prefix='/quotes', tags=['quotes'])

_provider = MockMarketDataProvider()


@router.get('/{symbol}')
async def get_quote(
    symbol: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    symbol_upper = symbol.upper()
    result = await session.execute(
        select(WatchlistEntry).where(WatchlistEntry.symbol == symbol_upper)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f'{symbol_upper} not in watchlist')

    snapshot = await session.execute(
        select(PriceSnapshot)
        .where(PriceSnapshot.symbol == symbol_upper)
        .order_by(PriceSnapshot.recorded_at.desc())
        .limit(1)
    )
    row = snapshot.scalar_one_or_none()
    if row is not None:
        return {
            'symbol': row.symbol,
            'price': row.price,
            'change_percent': row.change_percent,
            'provider': row.provider,
        }

    ts = TickerSymbol(value=symbol)
    quote = _provider.get_quote(ts)
    return {
        'symbol': quote.symbol,
        'price': quote.price,
        'change_percent': quote.change_percent,
        'provider': quote.provider,
    }
