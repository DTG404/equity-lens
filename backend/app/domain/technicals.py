from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import pandas_ta as ta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db as core_db
from app.domain.db_models import PriceHistory


async def compute_technicals(
    symbol: str,
    session: AsyncSession | None = None,
) -> dict[str, Any]:
    """Compute technical indicators for a symbol from price history."""
    sym = symbol.upper()

    if session is not None:
        return await _compute(sym, session)

    if core_db._async_session_factory is None:
        await core_db.init_db()
    assert core_db._async_session_factory is not None
    async with core_db._async_session_factory() as s:
        return await _compute(sym, s)


async def _compute(sym: str, session: AsyncSession) -> dict[str, Any]:
    result = await session.execute(
        select(PriceHistory)
        .where(PriceHistory.symbol == sym)
        .order_by(PriceHistory.date)
    )
    rows = result.scalars().all()

    if not rows:
        try:
            from app.domain.models import TickerSymbol
            from app.providers import get_market_data_provider
            ts = TickerSymbol(value=sym)
            provider = get_market_data_provider()
            history = provider.get_history(ts, days=90)
            for e in history:
                bar_date_str = e["date"][:10]
                session.add(
                    PriceHistory(
                        symbol=sym,
                        date=datetime.strptime(bar_date_str, "%Y-%m-%d").date(),
                        open_price=e["open"],
                        high_price=e["high"],
                        low_price=e["low"],
                        close_price=e["close"],
                        volume=int(e.get("volume", 0)),
                    )
                )
            await session.flush()
            result = await session.execute(
                select(PriceHistory)
                .where(PriceHistory.symbol == sym)
                .order_by(PriceHistory.date)
            )
            rows = result.scalars().all()
        except Exception:
            pass

    if not rows:
        return {"symbol": sym, "error": "No price history available"}

    df = pd.DataFrame(
        [
            {
                "date": r.date if hasattr(r.date, "isoformat") else str(r.date),
                "open": r.open_price,
                "high": r.high_price,
                "low": r.low_price,
                "close": r.close_price,
                "volume": r.volume,
            }
            for r in rows
        ]
    )

    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    rsi_series = ta.rsi(close, length=14)

    macd_result = ta.macd(close)
    macd_line = (
        macd_result.get("MACD_12_26_9", pd.Series())
        if macd_result is not None
        else pd.Series()
    )
    signal_line = (
        macd_result.get("MACDs_12_26_9", pd.Series())
        if macd_result is not None
        else pd.Series()
    )
    macd_histogram = (
        macd_result.get("MACDh_12_26_9", pd.Series())
        if macd_result is not None
        else pd.Series()
    )

    sma_20 = ta.sma(close, length=20)
    sma_50 = ta.sma(close, length=50)
    sma_200 = ta.sma(close, length=200)
    ema_12 = ta.ema(close, length=12)
    ema_26 = ta.ema(close, length=26)

    bb_result = ta.bbands(close)
    bb_upper = (
        bb_result.get("BBU_20_2.0", pd.Series())
        if bb_result is not None
        else pd.Series()
    )
    bb_middle = (
        bb_result.get("BBM_20_2.0", pd.Series())
        if bb_result is not None
        else pd.Series()
    )
    bb_lower = (
        bb_result.get("BBL_20_2.0", pd.Series())
        if bb_result is not None
        else pd.Series()
    )

    atr_series = ta.atr(high, low, close, length=14)

    stoch_result = ta.stoch(high, low, close)
    willr_series = ta.willr(high, low, close)
    mfi_series = ta.mfi(high, low, close, volume)
    cci_series = ta.cci(high, low, close)
    obv_series = ta.obv(close, volume)
    cmf_series = ta.cmf(high, low, close, volume)
    vwap_series = ta.vwap(high, low, close, volume)
    kc_result = ta.kc(high, low, close)
    psar_result = ta.psar(high, low, close)
    ichimoku_tup = ta.ichimoku(high, low, close)
    ichimoku_result = ichimoku_tup[0] if ichimoku_tup else None
    adx_result = ta.adx(high, low, close)
    aroon_result = ta.aroon(high, low, close)
    uo_series = ta.uo(high, low, close)
    trix_result = ta.trix(close)
    roc_series = ta.roc(close)
    mom_series = ta.mom(close)
    donchian_result = ta.donchian(high, low, close)
    kama_series = ta.kama(close)
    hma_series = ta.hma(close)
    supertrend_result = ta.supertrend(high, low, close)

    elder_ray_ema = ta.ema(close, length=13)
    ad_series = ta.ad(high, low, close, volume)

    def latest(series: pd.Series | None) -> float | None:
        if series is None or not isinstance(series, pd.Series):
            return None
        vals = series.dropna()
        return round(float(vals.iloc[-1]), 2) if len(vals) > 0 else None

    def col(df: pd.DataFrame | None, name: str) -> pd.Series | None:
        if df is None or name not in df.columns:
            return None
        return df[name]

    return {
        "symbol": sym,
        "rsi": latest(rsi_series),
        "macd": {
            "macd_line": latest(macd_line),
            "signal_line": latest(signal_line),
            "histogram": latest(macd_histogram),
        },
        "moving_averages": {
            "sma_20": latest(sma_20),
            "sma_50": latest(sma_50),
            "sma_200": latest(sma_200),
            "ema_12": latest(ema_12),
            "ema_26": latest(ema_26),
        },
        "bollinger_bands": {
            "upper": latest(bb_upper),
            "middle": latest(bb_middle),
            "lower": latest(bb_lower),
        },
        "atr": latest(atr_series),
        "stochastic": {
            "k": latest(col(stoch_result, "STOCHk_14_3_3")),
            "d": latest(col(stoch_result, "STOCHd_14_3_3")),
        },
        "williams_r": latest(willr_series),
        "mfi": latest(mfi_series),
        "cci": latest(cci_series),
        "obv": latest(obv_series),
        "cmf": latest(cmf_series),
        "vwap": latest(vwap_series),
        "keltner": {
            "upper": latest(col(kc_result, "KCUe_20_2")),
            "middle": latest(col(kc_result, "KCBe_20_2")),
            "lower": latest(col(kc_result, "KCLe_20_2")),
        },
        "parabolic_sar": latest(col(psar_result, "PSARl_0.02_0.2")),
        "ichimoku": {
            "conversion": latest(col(ichimoku_result, "ITS_9")),
            "base": latest(col(ichimoku_result, "IKS_26")),
            "span_a": latest(col(ichimoku_result, "ISA_9")),
            "span_b": latest(col(ichimoku_result, "ISB_26")),
        },
        "adx": latest(col(adx_result, "ADX_14")),
        "adx_positive_di": latest(col(adx_result, "DMP_14")),
        "adx_negative_di": latest(col(adx_result, "DMN_14")),
        "aroon": {
            "aroon_up": latest(col(aroon_result, "AROONU_14")),
            "aroon_down": latest(col(aroon_result, "AROOND_14")),
        },
        "ultimate_oscillator": latest(uo_series),
        "trix": latest(col(trix_result, "TRIX_30_9")),
        "roc": latest(roc_series),
        "momentum": latest(mom_series),
        "donchian": {
            "upper": latest(col(donchian_result, "DCU_20_20")),
            "middle": latest(col(donchian_result, "DCM_20_20")),
            "lower": latest(col(donchian_result, "DCL_20_20")),
        },
        "kama": latest(kama_series),
        "hma": latest(hma_series),
        "supertrend": latest(col(supertrend_result, "SUPERT_7_3.0")),
        "elder_ray": {
            "bull_power": latest(high - elder_ray_ema),
            "bear_power": latest(low - elder_ray_ema),
        },
        "ad_line": latest(ad_series),
    }
