# Findings

1. **[Blocker][API]** `apps/api/app/routers/live.py:15-32` — SSE endpoint only sends heartbeats and never subscribes to Redis, leaving live updates unimplemented.
2. **[Major][API]** `apps/api/app/deps.py:17-23` — SQLAlchemy `create_engine` uses `pool_size`/`max_overflow` options that break with SQLite during tests.
3. **[Major][API]** `apps/api/app/security.py:8-17` — TokenEncryptionService mixes bytes and str when deriving the Fernet key, triggering mypy type errors.
4. **[Major][Worker]** `services/worker/tasks.py:21-28` — Tasks import an `Injury` model that does not exist in `app.models`, causing ImportError.
5. **[Major][CI]** `apps/api/app/models.py:1` — `black --check` fails; at least 34 files require formatting.
