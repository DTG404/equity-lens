"""Market sector performance API endpoints."""

from typing import Any

from fastapi import APIRouter

from app.providers.screener import UNIVERSE

router = APIRouter(prefix='/markets', tags=['markets'])


@router.get('/sectors')
async def get_sector_performance(period: str = '1d') -> dict[str, Any]:
    """Return sector performance for the given period."""
    import yfinance as yf

    periods = {'1d': 1, '1w': 5, '1m': 21, '3m': 63, '1y': 252}
    days = periods.get(period, 1)

    sectors: dict[str, list[float]] = {}
    for symbol in UNIVERSE:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            sector = info.get('sector') or 'Other'
            hist = ticker.history(period=f'{max(days + 5, 5)}d')
            if len(hist) >= 2:
                start = float(hist['Close'].iloc[0])
                end = float(hist['Close'].iloc[-1])
                ret = round(((end - start) / start) * 100, 2) if start else 0
                if sector not in sectors:
                    sectors[sector] = []
                sectors[sector].append(ret)
        except Exception:
            pass

    result = []
    for sector, returns in sorted(sectors.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True):
        avg_ret = round(sum(returns) / len(returns), 2)
        result.append({
            'name': sector,
            'return_pct': avg_ret,
            'constituent_count': len(returns),
        })

    return {'period': period, 'sectors': result}
