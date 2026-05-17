from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from app.domain.models import TickerSymbol


class Quote(BaseModel):
    symbol: str
    price: float
    change_percent: float
    provider: str


class CompanyInfo(BaseModel):
    symbol: str
    company_name: str = ''
    sector: str = ''
    industry: str = ''
    description: str = ''


@runtime_checkable
class MarketDataProvider(Protocol):
    def get_quote(self, symbol: TickerSymbol) -> Quote: ...
    def get_company_info(self, symbol: TickerSymbol) -> CompanyInfo: ...
    def get_history(self, symbol: TickerSymbol, days: int = 90) -> list[dict]: ...
