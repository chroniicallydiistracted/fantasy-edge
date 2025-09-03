# PR Plan

1. **PR-1: Redis-backed SSE**
   - Replace placeholder logic in `apps/api/app/routers/live.py` with real Redis pub/sub implementation.
   - Tests: `ruff check apps/api/app/routers/live.py`, `black --check apps/api/app/routers/live.py`, `pytest tests/test_live.py` (new).

2. **PR-2: Lint and format cleanup**
   - Drop unused imports across API routers (`auth`, `events`, `leagues`, `preferences`, `team`) and run `black`.
   - Tests: `ruff check apps/api`, `black --check apps/api`, `mypy app`, `pytest`.

3. **PR-3: Worker model guards**
   - Gracefully handle optional `Injury`/`PlayerLink` models in worker tasks.
   - Tests: `ruff check services/worker`, `black --check services/worker`, `pytest services/worker`.

4. **PR-4: Dependency hygiene**
   - Remove unused root `package-lock.json` and web `package-lock.json` to rely solely on `pnpm-lock.yaml`.
   - Tests: `pnpm lint`, `pnpm build`.

5. **PR-5: Test isolation**

 - Mock Redis in OAuth tests to avoid external connections and stabilize CI.
  - Tests: `pytest tests/test_oauth.py`.
6. **PR-6: Type-checking stability**
   - Adopt SQLAlchemy 2.0 typing (`DeclarativeBase`, `Mapped`) and configure mypy to ignore missing Celery stubs.
   - Tests: `mypy apps/api/app`, `mypy services/worker`.
