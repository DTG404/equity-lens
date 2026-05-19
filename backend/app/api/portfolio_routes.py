"""Portfolio performance tracking and analytics endpoints."""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import CompanyInfo, Holding, PriceHistory, PriceSnapshot

router = APIRouter(prefix='/portfolio', tags=['portfolio'])


@router.get('/performance')
async def get_portfolio_performance(
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Calculate P&L for each holding using latest price data."""
    result = await session.execute(select(Holding))
    holdings = result.scalars().all()

    total_cost = 0.0
    total_value = 0.0
    positions: list[dict[str, Any]] = []

    for h in holdings:
        cost = h.quantity * h.average_cost
        total_cost += cost

        # Get latest price
        price_result = await session.execute(
            select(PriceSnapshot)
            .where(PriceSnapshot.symbol == h.symbol)
            .order_by(desc(PriceSnapshot.recorded_at))
            .limit(1)
        )
        snap = price_result.scalar_one_or_none()
        current_price = snap.price if snap else h.average_cost

        value = h.quantity * current_price
        total_value += value
        pl = value - cost
        pl_pct = (
            ((current_price - h.average_cost) / h.average_cost) * 100
            if h.average_cost else 0.0
        )

        positions.append({
            'symbol': h.symbol,
            'quantity': h.quantity,
            'avg_cost': round(h.average_cost, 2),
            'current_price': round(current_price, 2),
            'cost_basis': round(cost, 2),
            'market_value': round(value, 2),
            'pl': round(pl, 2),
            'pl_pct': round(pl_pct, 2),
        })

    total_pl = total_value - total_cost
    total_pl_pct = ((total_value / total_cost) - 1) * 100 if total_cost > 0 else 0.0

    return {
        'total_cost': round(total_cost, 2),
        'total_value': round(total_value, 2),
        'total_pl': round(total_pl, 2),
        'total_pl_pct': round(total_pl_pct, 2),
        'position_count': len(positions),
        'positions': positions,
    }


@router.get('/analytics')
async def get_portfolio_analytics(
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Calculate portfolio allocation and estimate value history."""
    result = await session.execute(select(Holding))
    holdings = result.scalars().all()

    if not holdings:
        return {
            'allocation': {
                'by_ticker': [],
                'by_sector': [],
                'total_value': 0.0,
            },
            'value_history': [],
            'benchmark': None,
        }

    symbols = [h.symbol for h in holdings]

    price_result = await session.execute(
        select(PriceSnapshot)
        .where(PriceSnapshot.symbol.in_(symbols))
        .order_by(PriceSnapshot.symbol, PriceSnapshot.recorded_at.desc())
    )
    latest_prices: dict[str, float] = {}
    for snap in price_result.scalars().all():
        if snap.symbol not in latest_prices:
            latest_prices[snap.symbol] = snap.price

    company_result = await session.execute(
        select(CompanyInfo).where(CompanyInfo.symbol.in_(symbols))
    )
    companies = {ci.symbol: ci for ci in company_result.scalars().all()}

    total_value = 0.0
    tickers: list[dict[str, Any]] = []
    sector_values: dict[str, float] = {}
    holding_map: dict[str, float] = {}

    for h in holdings:
        current_price = latest_prices.get(h.symbol, h.average_cost)
        market_value = h.quantity * current_price
        total_value += market_value
        holding_map[h.symbol] = h.quantity

        ci = companies.get(h.symbol)
        sector = ci.sector if (ci and ci.sector) else 'Unknown'

        tickers.append({
            'symbol': h.symbol,
            'quantity': h.quantity,
            'avg_cost': round(h.average_cost, 2),
            'market_value': round(market_value, 2),
            'pct': 0.0,
            'sector': sector,
        })
        sector_values[sector] = sector_values.get(sector, 0.0) + market_value

    for t in tickers:
        t['pct'] = round((t['market_value'] / total_value * 100), 2) if total_value else 0.0

    by_sector = [
        {
            'sector': sector,
            'market_value': round(value, 2),
            'pct': round((value / total_value * 100), 2) if total_value else 0.0,
        }
        for sector, value in sorted(sector_values.items(), key=lambda x: x[1], reverse=True)
    ]

    value_history: list[dict[str, Any]] = []

    price_history_result = await session.execute(
        select(PriceHistory)
        .where(PriceHistory.symbol.in_(symbols))
        .order_by(PriceHistory.date)
    )
    ph_rows = price_history_result.scalars().all()

    if ph_rows:
        date_prices: dict[date, dict[str, float]] = {}
        for ph in ph_rows:
            d = ph.date.date() if hasattr(ph.date, 'date') else ph.date
            if d not in date_prices:
                date_prices[d] = {}
            date_prices[d][ph.symbol] = ph.close_price

        for d in sorted(date_prices):
            portfolio_value = 0.0
            for symbol, qty in holding_map.items():
                close_price = date_prices[d].get(symbol)
                if close_price is not None:
                    portfolio_value += qty * close_price
            if portfolio_value > 0:
                value_history.append({
                    'date': d.isoformat(),
                    'value': round(portfolio_value, 2),
                })

    return {
        'allocation': {
            'by_ticker': tickers,
            'by_sector': by_sector,
            'total_value': round(total_value, 2),
        },
        'value_history': value_history,
        'benchmark': None,
    }
