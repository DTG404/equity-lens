"""Markets overview endpoint."""

from typing import Any

from fastapi import APIRouter

from app.providers.markets import get_markets_overview

router = APIRouter(prefix='/markets', tags=['markets'])


@router.get('/overview')
async def markets_overview() -> dict[str, Any]:
    """Return market indices, breadth, commodities, and global data."""
    return await get_markets_overview()
