"""WebSocket for live streaming quotes."""

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import desc, select

from app.core.db import _async_session_factory, init_db
from app.domain.db_models import PriceSnapshot, WatchlistEntry
from app.domain.models import TickerSymbol
from app.providers import get_market_data_provider

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket('/ws/quotes')
async def websocket_quotes(websocket: WebSocket) -> None:
    """Stream live quotes to connected clients every 5 seconds."""
    await websocket.accept()

    try:
        while True:
            # Get watchlist symbols
            if _async_session_factory is None:
                await init_db()
            assert _async_session_factory is not None

            async with _async_session_factory() as session:
                result = await session.execute(select(WatchlistEntry.symbol))
                symbols = [row[0] for row in result.all()]

            if not symbols:
                await websocket.send_json({'type': 'info', 'message': 'Watchlist is empty'})
                await asyncio.sleep(5)
                continue

            # Fetch latest prices
            provider = get_market_data_provider()
            quotes = []
            for sym in symbols:
                try:
                    ts = TickerSymbol(value=sym)
                    quote = provider.get_quote(ts)

                    # Also get previous close from DB
                    async with _async_session_factory() as session:
                        prev = await session.execute(
                            select(PriceSnapshot)
                            .where(PriceSnapshot.symbol == sym)
                            .order_by(desc(PriceSnapshot.recorded_at))
                            .limit(1)
                        )
                        snap = prev.scalar_one_or_none()

                    quotes.append({
                        'symbol': sym,
                        'price': quote.price,
                        'change_percent': quote.change_percent,
                        'provider': quote.provider,
                        'previous_close': snap.price if snap else None,
                    })
                except Exception as e:
                    logger.warning('WS poll failed for %s: %s', sym, e)

            await websocket.send_json({
                'type': 'quotes',
                'data': quotes,
                'timestamp': asyncio.get_event_loop().time(),
            })

            await asyncio.sleep(5)

    except WebSocketDisconnect:
        logger.info('WebSocket client disconnected')
    except Exception as e:
        logger.error('WebSocket error: %s', e)
        try:
            await websocket.send_json({'type': 'error', 'message': str(e)})
        except Exception:
            pass
