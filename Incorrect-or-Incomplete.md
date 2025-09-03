# Incorrect or Incomplete Items

- `apps/api/app/models.py:1-80` — uses legacy `declarative_base` without SQLAlchemy 2.0 `DeclarativeBase`/`Mapped` types, causing `mypy` to hang.
