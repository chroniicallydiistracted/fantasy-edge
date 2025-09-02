# PR Plan

1. **PR-1: Web build configuration**
   - Fix ESM exports for Next and PostCSS configs; remove redundant lockfile.
   - Tests: `pnpm lint`, `pnpm build`.

2. **PR-2: API waiver module cleanup**
   - Rename `waivers.py` to `waiver_service.py` and update imports to resolve MyPy collisions.
   - Tests: `ruff check`, `black --check`, `mypy app/`, `pytest`.

3. **PR-3: Enforce TLS defaults**
   - Update `redis_url` defaults in API and worker to `rediss://`; document in `.env.example`.
   - Tests: `ruff check` for API and worker.

4. **PR-4: CI and dependency hygiene**
   - Use `pnpm install` in web CI job and drop unused root `package.json`/lockfiles.
   - Tests: GitHub Actions workflow run on PR.

5. **PR-5: SSE endpoint implementation**
   - Replace placeholder logic in `apps/api/app/routers/live.py` with real Redis pub/sub and backoff.
   - Tests: `ruff check`, `black --check`, `mypy apps/api/app/routers/live.py`, `pytest`.

6. **PR-6: Database and worker cleanup**
   - Adjust SQLAlchemy engine options for SQLite tests and introduce missing `Injury` model or refactor worker imports.
   - Tests: `ruff check`, `black --check`, `mypy apps/api/app`, `pytest`.
