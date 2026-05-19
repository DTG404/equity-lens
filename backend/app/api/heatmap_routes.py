"""Sector heatmap endpoint returning hierarchical data for treemap visualization."""

from typing import Any

from fastapi import APIRouter

from app.providers.screener import UNIVERSE

router = APIRouter(prefix='/heatmap', tags=['heatmap'])

_heatmap_cache: dict[str, Any] = {}
_cache_ttl = 3600


@router.get('')
async def get_heatmap() -> dict[str, Any]:
    """Return hierarchical sector data for d3 treemap visualization."""
    import time

    now = time.time()
    if _heatmap_cache and (now - _heatmap_cache.get('_ts', 0)) < _cache_ttl:
        # Return cached data without the timestamp
        return {k: v for k, v in _heatmap_cache.items() if k != '_ts'}

    import yfinance as yf

    sectors: dict[str, dict[str, Any]] = {}

    for symbol in UNIVERSE:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            sector = info.get('sector') or 'Other'
            industry = info.get('industry') or 'Other'
            market_cap = info.get('marketCap') or 0
            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            prev_close = info.get('previousClose') or price or 1
            change_pct = round(((price - prev_close) / prev_close) * 100, 2) if prev_close else 0.0

            if sector not in sectors:
                sectors[sector] = {'name': sector, 'children': {}, 'market_cap': 0, 'change_pct': 0.0}

            if industry not in sectors[sector]['children']:
                sectors[sector]['children'][industry] = {
                    'name': industry, 'children': [], 'market_cap': 0, 'change_pct': 0.0,
                }

            sectors[sector]['children'][industry]['children'].append({
                'symbol': symbol,
                'name': info.get('shortName') or info.get('longName') or symbol,
                'market_cap': market_cap,
                'change_pct': change_pct,
                'sector': sector,
                'price': round(float(price), 2) if price else 0,
            })
            sectors[sector]['children'][industry]['market_cap'] += market_cap
            sectors[sector]['market_cap'] += market_cap

        except Exception:
            pass

    # Convert nested dicts to sorted lists
    result_children = []
    for sector_name, sector_data in sorted(
        sectors.items(), key=lambda x: x[1]['market_cap'], reverse=True,
    ):
        industry_list = []
        for ind_name, ind_data in sorted(
            sector_data['children'].items(), key=lambda x: x[1]['market_cap'], reverse=True,
        ):
            ind_data['children'].sort(key=lambda x: x['market_cap'], reverse=True)
            ind_data['change_pct'] = round(
                sum(c['change_pct'] for c in ind_data['children']) / len(ind_data['children']), 2
            ) if ind_data['children'] else 0.0
            industry_list.append(ind_data)

        if industry_list:
            child_sectors = [i for i in industry_list if i['children']]
            avg_change = sum(i['change_pct'] for i in child_sectors) / max(len(child_sectors), 1)
            sector_data['change_pct'] = round(avg_change, 2)
        else:
            sector_data['change_pct'] = 0.0
        result_children.append({
            'name': sector_name,
            'children': industry_list,
            'market_cap': sector_data['market_cap'],
            'change_pct': sector_data.get('change_pct', 0),
        })

    result: dict[str, Any] = {'children': result_children}
    result['_ts'] = now
    _heatmap_cache.clear()
    _heatmap_cache.update(result)
    # Return without timestamp
    return {k: v for k, v in result.items() if k != '_ts'}
