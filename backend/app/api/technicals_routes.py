from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.technicals import compute_technicals

router = APIRouter(prefix="/technicals", tags=["technicals"])


@router.get("/{symbol}")
async def get_technicals(
    symbol: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    data = await compute_technicals(symbol.upper(), session=session)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data
