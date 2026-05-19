"""Peer comparison API endpoint."""

from typing import Any

import yfinance as yf
from fastapi import APIRouter, HTTPException

from app.domain.models import TickerSymbol
from app.providers.screener import UNIVERSE

router = APIRouter(tags=['compare'])


@router.get('/peers/{symbol}')
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
