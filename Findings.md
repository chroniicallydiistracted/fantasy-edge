# Findings

1. **[Fixed][API]** `apps/api/app/routers/live.py` — SSE endpoint now subscribes to Redis with heartbeat fallback.
2. **[Fixed][API]** unused or duplicate imports removed across routers (`auth`, `events`, `leagues`, `preferences`, `team`).
3. **[Fixed][Worker]** `services/worker/tasks.py` guards optional `Injury`, `PlayerLink`, and `Weather` models and skips DB writes when missing.
4. **[Fixed][Web]** redundant `package-lock.json` files removed in favor of `pnpm-lock.yaml`.
5. **[Fixed][Auth]** OAuth tests seed env vars and fall back to `fakeredis`, avoiding external Redis connections.
6. **[Fixed][Auth]** `apps/api/tests/conftest.py` now overrides `REDIS_URL` to ensure tests never hit a live Redis instance.
7. **[Fixed][Auth]** `apps/api/app/settings.py` now provides safe defaults for required environment variables, allowing tests and static analysis without external configuration.
8. **[Fixed][Web]** Added root `package.json` and `pnpm-workspace.yaml` so `pnpm lint` and `pnpm build` run from the repository root.
9. **[Fixed][API]** `apps/api/app/models.py` now defines ORM attributes with SQLAlchemy 2.0 `Mapped`/`mapped_column`, eliminating `Column[...]` typing issues.
10. **[Fixed][API]** `apps/api/app/settings.py` now injects environment defaults explicitly, removing mypy `call-arg` warnings.
11. **[Fixed][CI]** Installed `types-python-jose` to satisfy missing stub errors for `jose` imports.
12. **[Known][CI]** `mypy` still reports type errors in session management and OAuth helpers.
