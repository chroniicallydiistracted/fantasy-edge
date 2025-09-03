# Findings

1. **[Fixed][API]** `apps/api/app/routers/live.py` — SSE endpoint now subscribes to Redis with heartbeat fallback.
2. **[Fixed][API]** unused or duplicate imports removed across routers (`auth`, `events`, `leagues`, `preferences`, `team`).
3. **[Fixed][Worker]** `services/worker/tasks.py` guards optional `Injury`, `PlayerLink`, and `Weather` models and skips DB writes when missing.
4. **[Fixed][Web]** redundant `package-lock.json` files removed in favor of `pnpm-lock.yaml`.
5. **[Fixed][Auth]** OAuth tests seed env vars and fall back to `fakeredis`, avoiding external Redis connections.
6. **[Fixed][Auth]** `apps/api/tests/conftest.py` now overrides `REDIS_URL` to ensure tests never hit a live Redis instance.
7. **[Known][CI]** `mypy` hangs for both API and worker modules; SQLAlchemy and Celery typings need configuration.

