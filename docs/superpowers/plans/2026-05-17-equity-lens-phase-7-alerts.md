# Equity Lens Phase 7: Alerts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add configurable price/news/signal/risk alerts with in-app notification center and history.

**Architecture:** Alert rules define conditions (type, threshold, direction). A background evaluation function checks rules against current data and creates AlertEvent records. The frontend shows an alert center with unread counts and supports browser notifications.

**Tech Stack:** Python, FastAPI, SQLAlchemy, Next.js, Browser Notification API.

---

## File Structure Changes

```
backend/
  app/
    domain/
      db_models.py                         # + AlertRule, AlertEvent models
    api/
      alert_routes.py                      # NEW: rules CRUD + events endpoints
    core/
      scheduler.py                         # MODIFY: add evaluate_alerts
  tests/
    test_alert_models.py                   # NEW: model tests
    test_alert_routes.py                   # NEW: API tests
    test_alert_evaluation.py              # NEW: evaluation logic tests
frontend/
  src/
    lib/
      api.ts                              # MODIFY: add alert types + functions
    components/
      AlertCenter.tsx                      # NEW: alert notification panel
      DashboardShell.tsx                   # MODIFY: integrate AlertCenter
  tests/
    dashboard.test.tsx                     # MODIFY: update for alert center
```

## Task 1: Alert DB Models

**Files:**
- Modify: `backend/app/domain/db_models.py`
- Create: `backend/tests/test_alert_models.py`

- [ ] **Step 1: Write failing alert model tests**

Create `backend/tests/test_alert_models.py` with round-trip tests for `AlertRule` and `AlertEvent`.

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_alert_models.py -q`

Expected: FAIL.

- [ ] **Step 3: Add AlertRule and AlertEvent models**

```python
class AlertRule(Base):
    __tablename__ = 'alert_rules'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    alert_type: Mapped[str] = mapped_column(String(20), nullable=False)
    condition: Mapped[str] = mapped_column(String(20), default='above')
    threshold: Mapped[float] = mapped_column(Float, default=0.0)
    enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AlertEvent(Base):
    __tablename__ = 'alert_events'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_id: Mapped[int] = mapped_column(Integer, nullable=True)
    symbol: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    alert_type: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default='info')
    read: Mapped[bool] = mapped_column(default=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/test_alert_models.py -q`

Expected: pass.

## Task 2: Alert Evaluation Logic

**Files:**
- Modify: `backend/app/core/scheduler.py`
- Create: `backend/tests/test_alert_evaluation.py`

- [ ] **Step 1: Write failing evaluation tests**

Create `backend/tests/test_alert_evaluation.py` with tests for:
- Evaluating price-above rule triggers event when price exceeds threshold
- Evaluating price-below rule triggers event when price is below threshold
- Rule with wrong symbol does not trigger
- Disabled rule does not trigger

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_alert_evaluation.py -q`

Expected: FAIL.

- [ ] **Step 3: Add evaluate_alerts to scheduler.py**

Add `evaluate_alerts(session)` function that:
- Queries all enabled alert rules
- For price rules: checks latest PriceSnapshot against threshold
- Creates AlertEvent when condition is met
- Returns count of new alerts

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/test_alert_evaluation.py -q`

Expected: pass.

## Task 3: Alert API Endpoints

**Files:**
- Create: `backend/app/api/alert_routes.py`
- Modify: `backend/app/api/routes.py`
- Create: `backend/tests/test_alert_routes.py`

- [ ] **Step 1: Write failing alert API tests**

Create `backend/tests/test_alert_routes.py` with tests for:
- GET /api/alerts/rules returns list
- POST /api/alerts/rules creates rule
- DELETE /api/alerts/rules/{id} removes rule
- GET /api/alerts/events returns history
- GET /api/alerts/events/unread-count returns count
- PATCH /api/alerts/events/{id}/read marks as read

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_alert_routes.py -q`

Expected: FAIL.

- [ ] **Step 3: Create alert routes**

Create `backend/app/api/alert_routes.py` with:
- GET /api/alerts/rules — list rules
- POST /api/alerts/rules — create rule (symbol, alert_type, condition, threshold)
- DELETE /api/alerts/rules/{id} — delete rule
- GET /api/alerts/events — list events (paginated, most recent first)
- GET /api/alerts/events/unread-count — returns {count}
- PATCH /api/alerts/events/{id}/read — mark single as read
- POST /api/alerts/events/read-all — mark all as read

Register router in routes.py.

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/test_alert_routes.py -q`

Expected: pass.

## Task 4: Frontend Alert Center

**Files:**
- Create: `frontend/src/components/AlertCenter.tsx`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/DashboardShell.tsx`
- Modify: `frontend/tests/dashboard.test.tsx`

- [ ] **Step 1: Add alert API types and functions**

Add to `frontend/src/lib/api.ts`:

```typescript
export interface AlertRule {
  id: number;
  symbol: string;
  alert_type: string;
  condition: string;
  threshold: number;
  enabled: boolean;
  created_at: string;
}

export interface AlertEvent {
  id: number;
  symbol: string;
  alert_type: string;
  message: string;
  severity: string;
  read: boolean;
  triggered_at: string;
}

export async function fetchAlertRules(): Promise<AlertRule[]> { ... }
export async function createAlertRule(symbol: string, alertType: string, condition: string, threshold: number): Promise<void> { ... }
export async function deleteAlertRule(id: number): Promise<void> { ... }
export async function fetchAlertEvents(): Promise<AlertEvent[]> { ... }
export async function fetchUnreadAlertCount(): Promise<number> { ... }
export async function markAlertRead(id: number): Promise<void> { ... }
export async function markAllAlertsRead(): Promise<void> { ... }
```

- [ ] **Step 2: Create AlertCenter component**

Create `frontend/src/components/AlertCenter.tsx` showing:
- Unread count badge
- Recent alert events list
- Each alert shows type icon, message, time, severity
- Mark as read button per event
- "Mark all read" button

- [ ] **Step 3: Integrate into DashboardShell**

Replace the existing Alerts placeholder section with the AlertCenter component.

- [ ] **Step 4: Update tests**

Update `dashboard.test.tsx` to test alert center rendering and unread badge.

- [ ] **Step 5: Run frontend verification**

Run: `cd frontend && npm test -- --run && npm run lint && npm run build`

Expected: all pass.

## Task 5: Final Verification

- [ ] **Run all backend tests**: `cd backend && uv run pytest -q`
- [ ] **Run backend lint**: `cd backend && uv run ruff check app tests`
- [ ] **Run backend typecheck**: `cd backend && uv run mypy app`
- [ ] **Run all frontend checks**: `cd frontend && npm test -- --run && npm run lint && npm run build`
- [ ] **Run gitleaks**: `gitleaks detect --source . --no-git --config .gitleaks.toml`
