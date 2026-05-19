from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

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
    def get_history(self, symbol: TickerSymbol, days: int = 90) -> list[dict[str, Any]]: ...


@dataclass
class BrokerPosition:
    symbol: str
    quantity: float
    avg_cost: float
    current_price: float
    market_value: float
    cost_basis: float
    pl_pct: float


@dataclass
class BrokerSyncResult:
    positions: list[BrokerPosition]
    portfolio_value: float
    cash: float
    equity: float
    position_count: int
    provider: str
    account_id: str = ''
    error: str = ''


@runtime_checkable
class BrokerProvider(Protocol):
    provider_name: str = ''

    def is_configured(self) -> bool: ...

    async def sync_portfolio(self) -> BrokerSyncResult: ...
