# Incorrect or Incomplete Items


- `apps/api/app/models.py:1-80` — uses legacy `declarative_base` without SQLAlchemy 2.0 `DeclarativeBase`/`Mapped` types, causing `mypy` to hang.
- `services/worker/tasks.py:1-60` — depends on `celery` interfaces lacking type stubs, leading `mypy` to stall.
- `./package.json` — missing at repository root; `pnpm` commands error with `No package.json was found`.
- `apps/api/app/settings.py:15-24` — required env variables have no safe defaults, so settings instantiation fails during static analysis.

