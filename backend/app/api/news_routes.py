"""News API endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import NewsArticle, WatchlistEntry

router = APIRouter(prefix='/news', tags=['news'])


@router.get('')
async def get_all_news(
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    result = await session.execute(
        select(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(50)
    )
    return [_article_to_dict(a) for a in result.scalars().all()]


@router.get('/{symbol}')
async def get_symbol_news(
    symbol: str,
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    sym = symbol.upper()
    entry = await session.execute(
        select(WatchlistEntry).where(WatchlistEntry.symbol == sym)
    )
    if entry.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f'{sym} not in watchlist')

    result = await session.execute(
        select(NewsArticle)
        .where(NewsArticle.symbol == sym)
        .order_by(NewsArticle.published_at.desc())
        .limit(25)
    )
    return [_article_to_dict(a) for a in result.scalars().all()]


def _article_to_dict(a: NewsArticle) -> dict[str, Any]:
    return {
        'id': a.id,
        'symbol': a.symbol,
        'title': a.title,
        'url': a.url,
        'source': a.source,
        'summary': a.summary,
        'published_at': a.published_at.isoformat() if a.published_at else None,
    }
