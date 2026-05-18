"""Signal outcome history and metrics API endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import SignalOutcome

router = APIRouter(prefix='/signals', tags=['signals'])


@router.get('/outcomes')
async def list_outcomes(
    symbol: str = Query('', description='Filter by symbol'),
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 50,
) -> list[dict[str, object]]:
    query = select(SignalOutcome).order_by(SignalOutcome.checked_at.desc()).offset(skip).limit(limit)
    if symbol:
        query = query.where(SignalOutcome.symbol == symbol.upper())
    result = await session.execute(query)
    outcomes = result.scalars().all()
    return [
        {
            'id': o.id,
            'symbol': o.symbol,
            'analysis_id': o.analysis_id,
            'stance': o.stance,
            'confidence': o.confidence,
            'price_at_analysis': o.price_at_analysis,
            'window': o.window,
            'price_at_check': o.price_at_check,
            'return_pct': o.return_pct,
            'correct': o.correct,
            'checked_at': o.checked_at.isoformat() if o.checked_at else '',
        }
        for o in outcomes
    ]


@router.get('/metrics')
async def get_metrics(
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    count_result = await session.execute(select(func.count(SignalOutcome.id)))
    total = count_result.scalar() or 0

    if total == 0:
        return {
            'total_signals': 0,
            'correct_count': 0,
            'accuracy_pct': 0.0,
            'avg_return': 0.0,
        }

    correct_result = await session.execute(
        select(func.count(SignalOutcome.id)).where(SignalOutcome.correct.is_(True))
    )
    correct = correct_result.scalar() or 0

    avg_result = await session.execute(select(func.avg(SignalOutcome.return_pct)))
    avg_raw = avg_result.scalar()
    avg_return = round(float(avg_raw), 2) if avg_raw is not None else 0.0

    accuracy_pct = round((correct / total) * 100, 2)

    return {
        'total_signals': total,
        'correct_count': correct,
        'accuracy_pct': accuracy_pct,
        'avg_return': avg_return,
    }
