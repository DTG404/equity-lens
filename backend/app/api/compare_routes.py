"""Multiticker comparison endpoint."""

from typing import Any

import yfinance as yf
from fastapi import APIRouter, HTTPException, Query

from app.domain.models import TickerSymbol
from app.providers import get_market_data_provider

router = APIRouter(prefix='/compare', tags=['compare'])

MAX_TICKERS = 5


@router.get('')
async def compare_tickers(
    tickers: str = Query(..., description='Comma-separated ticker symbols (max 5)'),
) -> dict[str, Any]:
    symbol_list = [s.strip().upper() for s in tickers.split(',') if s.strip()]

    if len(symbol_list) > MAX_TICKERS:
        raise HTTPException(status_code=422, detail=f'Maximum {MAX_TICKERS} tickers allowed')
    if len(symbol_list) < 2:
        raise HTTPException(status_code=422, detail='At least 2 tickers required')

    for s in symbol_list:
        TickerSymbol(value=s)

    provider = get_market_data_provider()
    metrics: dict[str, dict[str, Any]] = {}
    ticker_list: list[str] = []

    for symbol in symbol_list:
        try:
            ts = TickerSymbol(value=symbol)
            quote = provider.get_quote(ts)
        except Exception:
            continue

        metric: dict[str, Any] = {
            'price': quote.price,
            'change_pct': round(quote.change_percent, 2),
            'market_cap': 0,
            'pe_ratio': 0.0,
            'revenue_growth': 0.0,
            'profit_margin': 0.0,
            'rsi': 50.0,
            'sector': 'Unknown',
        }

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            hist = ticker.history(period='1mo')
            rsi_val = 50.0
            if len(hist) > 14:
                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0.0).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
                rs = gain / loss
                rsi_val = round(float(100 - (100 / (1 + rs.iloc[-1]))), 1) if rs.iloc[-1] != 0 else 50.0

            metric.update({
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': round(float(info.get('trailingPE') or info.get('forwardPE') or 0), 1),
                'revenue_growth': round(float(info.get('revenueGrowth') or 0) * 100, 1),
                'profit_margin': round(float(info.get('profitMargins') or 0) * 100, 1),
                'rsi': rsi_val,
                'sector': info.get('sector', 'Unknown'),
            })
        except Exception:
            pass

        metrics[symbol] = metric
        ticker_list.append(symbol)

    if not ticker_list:
        raise HTTPException(status_code=404, detail='No valid tickers found')

    best_values: dict[str, str] = {}
    for metric_key in ['market_cap', 'revenue_growth', 'profit_margin']:
        valid = {s: metrics[s][metric_key] for s in ticker_list if metrics[s].get(metric_key, 0)}
        if valid:
            best_values[metric_key] = max(valid, key=lambda s: valid[s])

    return {
        'tickers': ticker_list,
        'metrics': metrics,
        'best_values': best_values,
    }
