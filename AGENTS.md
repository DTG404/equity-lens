# Equity Lens

Local-first stock market research terminal.

## Commands

- Backend tests: `cd backend && uv run pytest`
- Backend lint: `cd backend && uv run ruff check app tests`
- Backend typecheck: `cd backend && uv run mypy app`
- Frontend tests: `cd frontend && npm test`
- Frontend lint: `cd frontend && npm run lint`
- Frontend build: `cd frontend && npm run build`
- Dependency audit: `cd frontend && npm audit --audit-level=high`
- Secrets scan: `gitleaks detect --source . --no-git`

## Ticket Workflow (HARD RULE — NO EXCEPTIONS)

1. **In Progress** — move ticket when starting work
2. **Local checks BEFORE any commit/PR:**
   - `cd backend && uv run ruff check app tests && uv run mypy app && uv run pytest -x -q`
   - `cd frontend && npx tsc --noEmit && npm test && npm run build`
   - ALL must pass before pushing
3. **Resolution comment** — post to ticket after implementation
4. **Create PR** — branch with changes, wait for CI green
5. **In Review** — move ticket only when PR is green and ready
6. **Done** — only after user confirms

## Database Migrations

- Create migration: `cd backend && uv run alembic revision --autogenerate -m "description"`
- Apply: `cd backend && uv run alembic upgrade head`
- Rollback one step: `cd backend && uv run alembic downgrade -1`
- Check for drift: `cd backend && uv run alembic check`
- View history: `cd backend && uv run alembic history`

## Security Notes

- Never commit provider API keys.
- Keep provider secrets in backend-local environment variables.
- MVP must not execute trades.
