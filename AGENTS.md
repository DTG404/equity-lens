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

## Security Notes

- Never commit provider API keys.
- Keep provider secrets in backend-local environment variables.
- MVP must not execute trades.
