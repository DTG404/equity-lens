from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from app.domain.models import TickerSymbol


class Quote(BaseModel):
    symbol: str
    price: float
    change_percent: float
    provider: str


@runtime_checkable
class MarketDataProvider(Protocol):
    def get_quote(self, symbol: TickerSymbol) -> Quote: ...
