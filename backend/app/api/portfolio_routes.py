"""Portfolio performance tracking endpoint."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import Holding, PriceSnapshot

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
        pl_pct = ((current_price - h.average_cost) / h.average_cost) * 100 if h.average_cost else 0.0

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
