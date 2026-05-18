# Graph Report - equity-lens  (2026-05-17)

## Corpus Check
- 95 files · ~105,061 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 485 nodes · 989 edges · 27 communities detected
- Extraction: 42% EXTRACTED · 58% INFERRED · 0% AMBIGUOUS · INFERRED: 577 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]

## God Nodes (most connected - your core abstractions)
1. `TickerSymbol` - 79 edges
2. `PriceSnapshot` - 60 edges
3. `Analysis` - 54 edges
4. `SignalOutcome` - 48 edges
5. `AlertRule` - 41 edges
6. `WatchlistEntry` - 38 edges
7. `NewsArticle` - 38 edges
8. `AlertEvent` - 37 edges
9. `PriceHistory` - 25 edges
10. `MockMarketDataProvider` - 24 edges

## Surprising Connections (you probably didn't know these)
- `TickerSymbol` --uses--> `Factor scoring for stock analysis.`  [INFERRED]
  backend/app/domain/models.py → backend/app/domain/scoring.py
- `TickerSymbol` --uses--> `Compute factor scores using real price/news data when available.      Technical`  [INFERRED]
  backend/app/domain/models.py → backend/app/domain/scoring.py
- `TickerSymbol` --uses--> `Simple deterministic pseudo-random for reproducible scoring.`  [INFERRED]
  backend/app/domain/models.py → backend/app/domain/scoring.py
- `TickerSymbol` --uses--> `NewsItem`  [INFERRED]
  backend/app/domain/models.py → backend/app/providers/news_base.py
- `TickerSymbol` --uses--> `News provider protocol and data model.`  [INFERRED]
  backend/app/domain/models.py → backend/app/providers/news_base.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.17
Nodes (60): AlertEvent, AlertRule, Analysis, Base, CompanyInfo, NewsArticle, PriceHistory, PriceSnapshot (+52 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (38): CompanyInfo, MarketDataProvider, Quote, get_market_data_provider(), get_news_provider(), Data provider dispatch — factory functions read settings to return correct provi, Return the configured market data provider., Return the configured market data provider. (+30 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (25): create_rule(), CreateRuleRequest, Alert rule and event API endpoints., BaseModel, Holding, Setting, add_holding(), HoldingCreateRequest (+17 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (33): close_db(), get_db_url(), get_session(), get_sync_db_url(), init_db(), Database engine, session factory, and FastAPI dependency., Return the database URL, converting common schemes for async access., Convert the async DB URL to a synchronous one for Alembic. (+25 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (17): handleAddRule(), handleDeleteRule(), handleMarkAllRead(), handleMarkRead(), loadAlerts(), createAlertRule(), deleteAlertRule(), fetchAlertEvents() (+9 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (22): get_fundamentals(), Fundamental data API endpoint., Fetch fundamental financial data for a symbol from SEC EDGAR., Stock screener — filters a predefined universe by user criteria., Screen the stock universe by the given criteria., Screen the stock universe by the given criteria., get_screener(), Stock screener API endpoint. (+14 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (8): evaluate_alerts(), test_evaluate_disabled_rule_does_not_trigger(), test_evaluate_price_above_triggers_event(), test_evaluate_price_below_triggers_event(), test_evaluate_wrong_symbol_does_not_trigger(), Tests for alert API endpoints., test_mark_all_events_read(), test_mark_event_read()

### Community 7 - "Community 7"
Cohesion: 0.16
Nodes (16): AnalysisInput, _build_fallback(), _build_prompt(), _call_deepseek_api(), generate_thesis(), DeepSeek-powered analysis service for thesis and scenario generation., Make an async call to the DeepSeek API., Build a structured fallback response when DeepSeek API is unavailable. (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.17
Nodes (13): compute_factor_scores(), Factor scoring for stock analysis., Compute factor scores using real price/news data when available.      Technical, Simple deterministic pseudo-random for reproducible scoring., _seeded_random(), Tests for factor scoring with data-driven computation., Technical score should increase with positive price change., News sentiment score should increase with positive average sentiment. (+5 more)

### Community 9 - "Community 9"
Cohesion: 0.22
Nodes (8): get_macro_data(), _get_sample_data(), FRED economic data provider for macroeconomic context., Fetch latest values for key economic indicators from FRED., Return sample data when FRED API key is not configured., get_macro(), Macroeconomic data API endpoint., Fetch latest macroeconomic indicators from FRED.

### Community 10 - "Community 10"
Cohesion: 0.25
Nodes (1): Tests for watchlist CRUD endpoints.

### Community 11 - "Community 11"
Cohesion: 0.25
Nodes (1): Tests for holdings CRUD endpoints.

### Community 12 - "Community 12"
Cohesion: 0.25
Nodes (1): Tests for settings key-value endpoints.

### Community 13 - "Community 13"
Cohesion: 0.25
Nodes (4): Tests for signal outcome API endpoints., test_list_outcomes_filters_by_symbol(), test_list_outcomes_with_data(), test_metrics_returns_accuracy_stats()

### Community 14 - "Community 14"
Cohesion: 0.32
Nodes (7): get_sync_url(), Alembic environment config — sync Alembic, async app, shared models., Convert the async DB URL to a sync-compatible one., Run migrations in 'offline' mode., Run migrations in 'online' mode with a sync engine., run_migrations_offline(), run_migrations_online()

### Community 15 - "Community 15"
Cohesion: 0.29
Nodes (3): override_get_session(), Test fixtures for async DB testing., Override the app's get_session dependency to use the test DB.

### Community 16 - "Community 16"
Cohesion: 0.33
Nodes (4): NewsItem, NewsProvider, News provider protocol and data model., Protocol

### Community 17 - "Community 17"
Cohesion: 0.33
Nodes (1): Tests for news API endpoints.

### Community 18 - "Community 18"
Cohesion: 0.33
Nodes (2): Tests for research aggregate endpoint., test_research_with_db_data_uses_real_scoring()

### Community 19 - "Community 19"
Cohesion: 0.4
Nodes (1): Tests for quote endpoints.

### Community 20 - "Community 20"
Cohesion: 0.4
Nodes (4): Tests for the Analysis ORM model., test_analysis_defaults(), test_analysis_multiple_per_symbol(), test_analysis_round_trip()

### Community 21 - "Community 21"
Cohesion: 0.83
Nodes (3): _article_to_dict(), get_all_news(), get_symbol_news()

### Community 22 - "Community 22"
Cohesion: 0.5
Nodes (1): Signal outcome history and metrics API endpoints.

### Community 23 - "Community 23"
Cohesion: 0.5
Nodes (3): Tests for NewsArticle model., test_news_article_deduplicates_by_url(), test_news_article_round_trip()

### Community 24 - "Community 24"
Cohesion: 0.5
Nodes (3): Tests for SignalOutcome model., test_signal_outcome_defaults(), test_signal_outcome_round_trip()

### Community 25 - "Community 25"
Cohesion: 0.5
Nodes (1): initial  Revision ID: 1c4a6e0040e6 Revises:  Create Date: 2026-05-17 15:31:34.53

### Community 26 - "Community 26"
Cohesion: 0.67
Nodes (2): BaseSettings, Settings

## Knowledge Gaps
- **34 isolated node(s):** `DeepSeek-powered analysis service for thesis and scenario generation.`, `Build a structured fallback response when DeepSeek API is unavailable.`, `Build the structured prompt for the DeepSeek API.`, `Generate investment thesis and scenarios using DeepSeek or fallback.      If DEE`, `Make an async call to the DeepSeek API.` (+29 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 10`** (8 nodes): `test_watchlist_crud.py`, `client()`, `Tests for watchlist CRUD endpoints.`, `test_add_duplicate_symbol_returns_error()`, `test_add_invalid_ticker_returns_error()`, `test_add_watchlist_entry()`, `test_delete_watchlist_entry()`, `test_list_watchlist_returns_added_entries()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (8 nodes): `test_holdings.py`, `client()`, `Tests for holdings CRUD endpoints.`, `test_add_holding()`, `test_add_holding_invalid_symbol_returns_422()`, `test_delete_holding()`, `test_list_holdings()`, `test_update_holding()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (8 nodes): `test_settings.py`, `client()`, `Tests for settings key-value endpoints.`, `test_get_setting_by_key()`, `test_get_setting_by_key_not_found()`, `test_get_settings_returns_empty()`, `test_put_and_get_setting()`, `test_put_settings_empty_key_returns_422()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (6 nodes): `test_news_routes.py`, `client()`, `Tests for news API endpoints.`, `test_get_aggregated_news()`, `test_get_news_for_unwatched_symbol_returns_404()`, `test_get_news_for_watched_symbol()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (6 nodes): `test_research_routes.py`, `client()`, `Tests for research aggregate endpoint.`, `test_research_for_unwatched_returns_404()`, `test_research_returns_aggregated_data()`, `test_research_with_db_data_uses_real_scoring()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (5 nodes): `test_quote_routes.py`, `client()`, `Tests for quote endpoints.`, `test_get_latest_quote_for_watched_symbol()`, `test_get_quote_for_unwatched_symbol_returns_404()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (4 nodes): `signals_routes.py`, `get_metrics()`, `list_outcomes()`, `Signal outcome history and metrics API endpoints.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (4 nodes): `downgrade()`, `initial  Revision ID: 1c4a6e0040e6 Revises:  Create Date: 2026-05-17 15:31:34.53`, `upgrade()`, `1c4a6e0040e6_initial.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (3 nodes): `config.py`, `BaseSettings`, `Settings`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TickerSymbol` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 7`, `Community 8`, `Community 16`?**
  _High betweenness centrality (0.165) - this node is a cross-community bridge._
- **Why does `PriceSnapshot` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 6`, `Community 18`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `compute_technicals()` connect `Community 5` to `Community 3`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 77 inferred relationships involving `TickerSymbol` (e.g. with `Background scheduler for periodic quote polling.` and `Poll quotes for all watchlist entries and store in PriceSnapshot.`) actually correct?**
  _`TickerSymbol` has 77 INFERRED edges - model-reasoned connections that need verification._
- **Are the 58 inferred relationships involving `PriceSnapshot` (e.g. with `Background scheduler for periodic quote polling.` and `Poll quotes for all watchlist entries and store in PriceSnapshot.`) actually correct?**
  _`PriceSnapshot` has 58 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `Analysis` (e.g. with `Background scheduler for periodic quote polling.` and `Poll quotes for all watchlist entries and store in PriceSnapshot.`) actually correct?**
  _`Analysis` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `SignalOutcome` (e.g. with `Background scheduler for periodic quote polling.` and `Poll quotes for all watchlist entries and store in PriceSnapshot.`) actually correct?**
  _`SignalOutcome` has 46 INFERRED edges - model-reasoned connections that need verification._