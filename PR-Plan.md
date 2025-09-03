# PR Plan

1. **PR-1: Type-checking stability**
   - Refactor API models to SQLAlchemy 2.0 `DeclarativeBase`/`Mapped` forms and provide Celery stubs or ignores so `mypy` completes.
   - Tests: `mypy apps/api/app`, `mypy services/worker`, `pytest`.

2. **PR-2: Redis/SSE tests**
   - Add deterministic tests for Redis fallback and live SSE streaming to guard against regressions.
   - Tests: `pytest tests/test_live.py` (new), `pytest services/worker/tests`.
