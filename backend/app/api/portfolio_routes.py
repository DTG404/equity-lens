"""Portfolio performance tracking endpoint."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import Holding, PriceHistory, PriceSnapshot

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
    """Compute portfolio analytics including allocation, value history, and risk metrics."""
    result = await session.execute(select(Holding))
    holdings = result.scalars().all()

    if not holdings:
        return {
            'allocation': {},
            'value_history': [],
            'risk_metrics': None,
        }

    symbols = [h.symbol for h in holdings]
    total_value = 0.0
    position_values: dict[str, float] = {}
    current_prices: dict[str, float] = {}

    for h in holdings:
        price_result = await session.execute(
            select(PriceSnapshot)
            .where(PriceSnapshot.symbol == h.symbol)
            .order_by(desc(PriceSnapshot.recorded_at))
            .limit(1),
        )
        snap = price_result.scalar_one_or_none()
        current_price = snap.price if snap else h.average_cost
        value = h.quantity * current_price
        total_value += value
        position_values[h.symbol] = value
        current_prices[h.symbol] = current_price

    by_ticker: list[dict[str, Any]] = []
    by_sector_map: dict[str, float] = {}
    for h in holdings:
        val = position_values.get(h.symbol, 0)
        pct = round((val / total_value * 100) if total_value > 0 else 0, 2)
        sector = 'Unknown'
        try:
            from app.domain.db_models import CompanyInfo
            ci_result = await session.execute(
                select(CompanyInfo).where(CompanyInfo.symbol == h.symbol)
            )
            ci = ci_result.scalar_one_or_none()
            if ci and ci.sector:
                sector = ci.sector
        except Exception:
            pass
        by_ticker.append({
            'symbol': h.symbol,
            'quantity': h.quantity,
            'avg_cost': h.average_cost,
            'current_price': current_prices.get(h.symbol, 0),
            'market_value': round(val, 2),
            'pct': pct,
            'sector': sector,
        })
        by_sector_map[sector] = by_sector_map.get(sector, 0) + val

    by_sector = [
        {'sector': s, 'market_value': round(v, 2), 'pct': round((v / total_value * 100), 1) if total_value > 0 else 0}
        for s, v in sorted(by_sector_map.items(), key=lambda x: x[1], reverse=True)
    ]

    allocation = {
        'by_ticker': by_ticker,
        'by_sector': by_sector,
        'total_value': round(total_value, 2),
    }

    # Build value history from daily price data
    value_history: list[dict[str, Any]] = []
    price_data: dict[str, dict[str, float]] = {}
    for symbol in symbols:
        ph_result = await session.execute(
            select(PriceHistory)
            .where(PriceHistory.symbol == symbol)
            .order_by(PriceHistory.date),
        )
        records = ph_result.scalars().all()
        price_data[symbol] = {str(r.date).split()[0]: r.close_price for r in records}

    all_dates: set[str] = set()
    for data in price_data.values():
        all_dates.update(data.keys())

    for date_str in sorted(all_dates):
        total = 0.0
        has_all = True
        for h in holdings:
            close = price_data.get(h.symbol, {}).get(date_str)
            if close is not None:
                total += h.quantity * close
            else:
                has_all = False
                break
        if has_all and total > 0:
            value_history.append({'date': date_str, 'value': round(total, 2)})

    # Default risk metrics (overridden when enough price history exists)
    risk_metrics = {
        'sharpe_ratio': 0.0,
        'max_drawdown_pct': 0.0,
        'volatility_annualized_pct': 0.0,
        'beta': 0.0,
        'alpha_pct': 0.0,
    }

    if len(value_history) >= 5:
        import math

        values = [v['value'] for v in value_history]
        daily_returns: list[float] = []
        for i in range(1, len(values)):
            if values[i - 1] > 0:
                daily_returns.append((values[i] - values[i - 1]) / values[i - 1])

        if daily_returns:
            import statistics

            avg_daily_return = statistics.mean(daily_returns)
            daily_volatility = statistics.stdev(daily_returns) if len(daily_returns) > 1 else 0

            risk_free_rate = 0.045
            daily_rfr = risk_free_rate / 252
            if daily_volatility > 0:
                sharpe = (avg_daily_return - daily_rfr) / daily_volatility * math.sqrt(252)
            else:
                sharpe = 0.0

            peak = values[0]
            max_dd = 0.0
            for v in values:
                if v > peak:
                    peak = v
                dd = (peak - v) / peak
                if dd > max_dd:
                    max_dd = dd

            ann_vol = daily_volatility * math.sqrt(252)

            risk_metrics = {
                'sharpe_ratio': round(sharpe, 2),
                'max_drawdown_pct': round(-max_dd * 100, 2),
                'volatility_annualized_pct': round(ann_vol * 100, 2),
                'beta': 0.0,
                'alpha_pct': 0.0,
            }

    return {
        'allocation': allocation,
        'value_history': value_history,
        'risk_metrics': risk_metrics,
    }
