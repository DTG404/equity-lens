"""Technical indicator calculations using pandas-ta."""

from typing import Any

import pandas as pd
import pandas_ta as ta
from sqlalchemy import select

from app.core import db as core_db
from app.domain.db_models import PriceHistory


async def compute_technicals(symbol: str) -> dict[str, Any]:
    """Compute technical indicators for a symbol from price history."""
    if core_db._async_session_factory is None:
        await core_db.init_db()
    assert core_db._async_session_factory is not None

    async with core_db._async_session_factory() as session:
        result = await session.execute(
            select(PriceHistory)
            .where(PriceHistory.symbol == symbol.upper())
            .order_by(PriceHistory.date)
        )
        rows = result.scalars().all()

    if not rows:
        return {'symbol': symbol.upper(), 'error': 'No price history available'}

    df = pd.DataFrame([
        {
            'date': r.date if hasattr(r.date, 'isoformat') else str(r.date),
            'open': r.open_price,
            'high': r.high_price,
            'low': r.low_price,
            'close': r.close_price,
            'volume': r.volume,
        }
        for r in rows
    ])

    close = df['close']

    # RSI (14-day)
    rsi_series = ta.rsi(close, length=14)

    # MACD
    macd_result = ta.macd(close)
    macd_line = macd_result.get('MACD_12_26_9', pd.Series()) if macd_result is not None else pd.Series()
    signal_line = macd_result.get('MACDs_12_26_9', pd.Series()) if macd_result is not None else pd.Series()
    macd_histogram = macd_result.get('MACDh_12_26_9', pd.Series()) if macd_result is not None else pd.Series()

    # Moving Averages
    sma_20 = ta.sma(close, length=20)
    sma_50 = ta.sma(close, length=50)
    sma_200 = ta.sma(close, length=200)
    ema_12 = ta.ema(close, length=12)
    ema_26 = ta.ema(close, length=26)

    # Bollinger Bands
    bb_result = ta.bbands(close)
    bb_upper = bb_result.get('BBU_20_2.0', pd.Series()) if bb_result is not None else pd.Series()
    bb_middle = bb_result.get('BBM_20_2.0', pd.Series()) if bb_result is not None else pd.Series()
    bb_lower = bb_result.get('BBL_20_2.0', pd.Series()) if bb_result is not None else pd.Series()

    # ATR (14-day)
    atr_series = ta.atr(df['high'], df['low'], close, length=14)

    # Get latest values
    def latest(series: pd.Series | None) -> float | None:
        if series is None:
            return None
        vals = series.dropna()
        return round(float(vals.iloc[-1]), 2) if len(vals) > 0 else None

    return {
        'symbol': symbol.upper(),
        'rsi': latest(rsi_series),
        'macd': {
            'macd_line': latest(macd_line),
            'signal_line': latest(signal_line),
            'histogram': latest(macd_histogram),
        },
        'moving_averages': {
            'sma_20': latest(sma_20),
            'sma_50': latest(sma_50),
            'sma_200': latest(sma_200),
            'ema_12': latest(ema_12),
            'ema_26': latest(ema_26),
        },
        'bollinger_bands': {
            'upper': latest(bb_upper),
            'middle': latest(bb_middle),
            'lower': latest(bb_lower),
        },
        'atr': latest(atr_series),
    }
