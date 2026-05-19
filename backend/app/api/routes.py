from fastapi import APIRouter, Depends

from app.api.alert_routes import router as alert_router
from app.api.backtest_routes import router as backtest_router
from app.api.broker_routes import router as broker_router
from app.api.compare_routes import router as compare_router
from app.api.csv_routes import router as csv_router
from app.api.dcf_routes import router as dcf_router
from app.api.finnhub_routes import router as finnhub_router
from app.api.fundamentals_routes import router as fundamentals_router
from app.api.heatmap_routes import router as heatmap_router
from app.api.holdings_routes import router as holdings_router
from app.api.macro_routes import router as macro_router
from app.api.markets_routes import router as markets_router
from app.api.news_routes import router as news_router
from app.api.notifications_routes import router as notifications_router
from app.api.pattern_routes import router as pattern_router
from app.api.portfolio_routes import router as portfolio_router
from app.api.quote_routes import router as quote_router
from app.api.research_routes import router as research_router
from app.api.screener_routes import router as screener_router
from app.api.sec_routes import router as sec_router
from app.api.settings_routes import router as settings_router
from app.api.signals_routes import router as signals_router
from app.api.social_routes import router as social_router
from app.api.technicals_routes import router as technicals_router
from app.api.watchlist_routes import router as watchlist_router
from app.core.auth import verify_api_key

# Public router for unauthenticated endpoints
public_router = APIRouter()


@public_router.get('/health')
def health() -> dict[str, str]:
    return {
        'service': 'equity-lens-api',
        'status': 'ok',
        'mode': 'local-first',
    }


# Main router with optional API key auth
router = APIRouter(dependencies=[Depends(verify_api_key)])
router.include_router(portfolio_router)
router.include_router(watchlist_router)
router.include_router(broker_router)
router.include_router(holdings_router)
router.include_router(research_router)
router.include_router(settings_router)
router.include_router(quote_router)
router.include_router(news_router)
router.include_router(alert_router)
router.include_router(backtest_router)
router.include_router(compare_router)
router.include_router(csv_router)
router.include_router(dcf_router)
router.include_router(finnhub_router)
router.include_router(fundamentals_router)
router.include_router(heatmap_router)
router.include_router(signals_router)
router.include_router(macro_router)
router.include_router(markets_router)
router.include_router(screener_router)
router.include_router(sec_router, prefix='/sec')
router.include_router(social_router)
router.include_router(technicals_router)
router.include_router(notifications_router)
router.include_router(pattern_router)
