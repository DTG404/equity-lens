"""Multiticker comparison and peer comparison endpoints."""

from typing import Any

import yfinance as yf
from fastapi import APIRouter, HTTPException, Query

from app.domain.models import TickerSymbol
from app.providers import get_market_data_provider
from app.providers.screener import UNIVERSE

router = APIRouter(prefix='/compare', tags=['compare'])
peers_router = APIRouter(prefix='/peers', tags=['peers'])

MAX_TICKERS = 5


@router.get('')
async def compare_tickers(
    tickers: str = Query(..., description='Comma-separated ticker symbols (max 5)'),
) -> dict[str, Any]:
    """Compare multiple tickers side by side."""
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


@peers_router.get('/{symbol}')
async def get_peers(symbol: str) -> dict[str, Any]:
    """Return peer comparison data for a symbol."""
    sym = symbol.upper()
    TickerSymbol(value=sym)

    ticker = yf.Ticker(sym)
    info = ticker.info or {}
    sector = info.get('sector', '')

    if not sector:
        raise HTTPException(status_code=404, detail=f'Could not determine sector for {sym}')

    peers = []
    for peer_sym in UNIVERSE:
        if peer_sym == sym:
            continue
        try:
            peer = yf.Ticker(peer_sym)
            peer_info = peer.info or {}
            if peer_info.get('sector') == sector:
                peers.append({
                    'symbol': peer_sym,
                    'name': peer_info.get('shortName') or peer_info.get('longName') or peer_sym,
                    'market_cap': peer_info.get('marketCap', 0),
                    'pe_ratio': peer_info.get('trailingPE') or peer_info.get('forwardPE') or 0,
                    'revenue_growth': (peer_info.get('revenueGrowth') or 0) * 100,
                    'profit_margin': (peer_info.get('profitMargins') or 0) * 100,
                    'rsi': 50.0,
                    'ytd_return': (peer_info.get('52WeekChange') or 0) * 100,
                })
        except Exception:
            pass

    peers.sort(key=lambda p: p['market_cap'], reverse=True)
    peers = peers[:10]

    ticker_info = info
    symbol_metrics = {
        'market_cap': ticker_info.get('marketCap', 0),
        'pe_ratio': ticker_info.get('trailingPE') or ticker_info.get('forwardPE') or 0,
        'revenue_growth': (ticker_info.get('revenueGrowth') or 0) * 100,
        'profit_margin': (ticker_info.get('profitMargins') or 0) * 100,
        'ytd_return': (ticker_info.get('52WeekChange') or 0) * 100,
    }

    percentiles = {}
    for metric in ['pe_ratio', 'revenue_growth', 'profit_margin', 'ytd_return']:
        values = [p[metric] for p in peers] + [symbol_metrics[metric]]
        ranked = sorted(values)
        my_rank = ranked.index(symbol_metrics[metric]) + 1
        percentiles[metric] = round((my_rank / len(ranked)) * 100)

    return {
        'symbol': sym,
        'sector': sector,
        'peers': peers,
        'symbol_metrics': symbol_metrics,
        'percentiles': percentiles,
    }
