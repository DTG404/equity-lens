"""Stock screener API endpoint — filters, presets, and CSV export."""

import csv
import io
import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import Setting
from app.providers.screener import screen_stocks

router = APIRouter(prefix='/screener', tags=['screener'])


class PresetCreateRequest(BaseModel):
    name: str
    filters: dict[str, Any]


PRESET_PREFIX = 'screener_preset_'


@router.get('')
async def get_screener(
    price_min: float | None = Query(None, alias='priceMin'),
    price_max: float | None = Query(None, alias='priceMax'),
    sector: str | None = None,
    rsi_min: float | None = Query(None, alias='rsiMin'),
    rsi_max: float | None = Query(None, alias='rsiMax'),
    volume_min: int | None = Query(None, alias='volumeMin'),
    # Valuation
    min_pe: float | None = Query(None, alias='minPe'),
    max_pe: float | None = Query(None, alias='maxPe'),
    min_ps: float | None = Query(None, alias='minPs'),
    max_ps: float | None = Query(None, alias='maxPs'),
    min_pb: float | None = Query(None, alias='minPb'),
    max_pb: float | None = Query(None, alias='maxPb'),
    # Financial health
    max_debt_to_equity: float | None = Query(None, alias='maxDebtToEquity'),
    min_profit_margin: float | None = Query(None, alias='minProfitMargin'),
    min_revenue_growth: float | None = Query(None, alias='minRevenueGrowth'),
    # Market metrics
    min_market_cap: float | None = Query(None, alias='minMarketCap'),
    max_market_cap: float | None = Query(None, alias='maxMarketCap'),
    min_beta: float | None = Query(None, alias='minBeta'),
    max_beta: float | None = Query(None, alias='maxBeta'),
    # Ownership
    min_short_float: float | None = Query(None, alias='minShortFloat'),
    max_short_float: float | None = Query(None, alias='maxShortFloat'),
    min_inst_ownership: float | None = Query(None, alias='minInstOwnership'),
    # Dividends
    min_dividend_yield: float | None = Query(None, alias='minDividendYield'),
    max_dividend_yield: float | None = Query(None, alias='maxDividendYield'),
    sort_by: str = Query('symbol', alias='sortBy'),
    sort_dir: str = Query('asc', alias='sortDir'),
    limit: int = 50,
    skip: int = 0,
) -> dict[str, Any]:
    """Screen the stock universe by price, sector, RSI, volume, and expanded filters."""
    return await screen_stocks(
        price_min=price_min,
        price_max=price_max,
        sector=sector,
        rsi_min=rsi_min,
        rsi_max=rsi_max,
        volume_min=volume_min,
        pe_min=min_pe,
        pe_max=max_pe,
        ps_min=min_ps,
        ps_max=max_ps,
        pb_min=min_pb,
        pb_max=max_pb,
        max_debt_to_equity=max_debt_to_equity,
        min_profit_margin=min_profit_margin,
        min_revenue_growth=min_revenue_growth,
        market_cap_min=min_market_cap,
        market_cap_max=max_market_cap,
        beta_min=min_beta,
        beta_max=max_beta,
        short_float_min=min_short_float,
        short_float_max=max_short_float,
        min_inst_ownership=min_inst_ownership,
        dividend_yield_min=min_dividend_yield,
        dividend_yield_max=max_dividend_yield,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
        skip=skip,
    )


@router.get('/export')
async def export_screener_csv(
    price_min: float | None = Query(None, alias='priceMin'),
    price_max: float | None = Query(None, alias='priceMax'),
    sector: str | None = None,
    rsi_min: float | None = Query(None, alias='rsiMin'),
    rsi_max: float | None = Query(None, alias='rsiMax'),
    volume_min: int | None = Query(None, alias='volumeMin'),
    min_pe: float | None = Query(None, alias='minPe'),
    max_pe: float | None = Query(None, alias='maxPe'),
    min_ps: float | None = Query(None, alias='minPs'),
    max_ps: float | None = Query(None, alias='maxPs'),
    min_pb: float | None = Query(None, alias='minPb'),
    max_pb: float | None = Query(None, alias='maxPb'),
    max_debt_to_equity: float | None = Query(None, alias='maxDebtToEquity'),
    min_profit_margin: float | None = Query(None, alias='minProfitMargin'),
    min_revenue_growth: float | None = Query(None, alias='minRevenueGrowth'),
    min_market_cap: float | None = Query(None, alias='minMarketCap'),
    max_market_cap: float | None = Query(None, alias='maxMarketCap'),
    min_beta: float | None = Query(None, alias='minBeta'),
    max_beta: float | None = Query(None, alias='maxBeta'),
    min_short_float: float | None = Query(None, alias='minShortFloat'),
    max_short_float: float | None = Query(None, alias='maxShortFloat'),
    min_inst_ownership: float | None = Query(None, alias='minInstOwnership'),
    min_dividend_yield: float | None = Query(None, alias='minDividendYield'),
    max_dividend_yield: float | None = Query(None, alias='maxDividendYield'),
    sort_by: str = Query('symbol', alias='sortBy'),
    sort_dir: str = Query('asc', alias='sortDir'),
    limit: int = 500,
    skip: int = 0,
) -> Any:
    """Export screener results as CSV."""
    data = await screen_stocks(
        price_min=price_min,
        price_max=price_max,
        sector=sector,
        rsi_min=rsi_min,
        rsi_max=rsi_max,
        volume_min=volume_min,
        pe_min=min_pe,
        pe_max=max_pe,
        ps_min=min_ps,
        ps_max=max_ps,
        pb_min=min_pb,
        pb_max=max_pb,
        max_debt_to_equity=max_debt_to_equity,
        min_profit_margin=min_profit_margin,
        min_revenue_growth=min_revenue_growth,
        market_cap_min=min_market_cap,
        market_cap_max=max_market_cap,
        beta_min=min_beta,
        beta_max=max_beta,
        short_float_min=min_short_float,
        short_float_max=max_short_float,
        min_inst_ownership=min_inst_ownership,
        dividend_yield_min=min_dividend_yield,
        dividend_yield_max=max_dividend_yield,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
        skip=skip,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    columns = [
        'symbol', 'name', 'price', 'change_percent', 'volume', 'sector',
        'market_cap', 'pe_ratio', 'ps_ratio', 'pb_ratio',
        'debt_to_equity', 'profit_margin', 'revenue_growth',
        'beta', 'short_float', 'inst_ownership', 'dividend_yield', 'rsi',
    ]
    writer.writerow(columns)
    for row in data['results']:
        writer.writerow([row.get(col, '') for col in columns])

    from fastapi.responses import Response
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=screener_results.csv'},
    )


@router.get('/presets')
async def list_presets(
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    """List saved screener presets."""
    result = await session.execute(
        select(Setting).where(Setting.key.like(f'{PRESET_PREFIX}%'))
    )
    settings = result.scalars().all()
    presets: list[dict[str, Any]] = []
    for s in settings:
        name = s.key[len(PRESET_PREFIX):]
        try:
            filters = json.loads(s.value)
        except (json.JSONDecodeError, TypeError):
            filters = {}
        presets.append({'name': name, 'filters': filters})
    return presets


@router.post('/presets')
async def create_preset(
    body: PresetCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Save a screener preset."""
    db_key = f'{PRESET_PREFIX}{body.name}'
    existing = await session.execute(
        select(Setting).where(Setting.key == db_key)
    )
    setting = existing.scalar_one_or_none()
    value = json.dumps(body.filters)
    if setting is not None:
        setting.value = value
    else:
        session.add(Setting(key=db_key, value=value))
    await session.flush()
    return {'name': body.name, 'filters': body.filters}


@router.delete('/presets/{name}')
async def delete_preset(
    name: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """Delete a screener preset."""
    db_key = f'{PRESET_PREFIX}{name}'
    existing = await session.execute(
        select(Setting).where(Setting.key == db_key)
    )
    setting = existing.scalar_one_or_none()
    if setting is None:
        raise HTTPException(status_code=404, detail=f'Preset "{name}" not found')
    await session.delete(setting)
    await session.flush()
    return {'status': 'deleted', 'name': name}
