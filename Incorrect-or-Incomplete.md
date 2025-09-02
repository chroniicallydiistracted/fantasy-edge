# Incorrect or Incomplete Items

- `apps/api/app/routers/live.py:15-32` — placeholder Redis connection; SSE stream lacks real pub/sub implementation.
- `apps/api/app/deps.py:17-23` — engine configuration uses `pool_size` and `max_overflow` incompatible with SQLite tests.
- `apps/api/app/security.py:8-17` — improper byte/string handling when encoding the Fernet key.
- `services/worker/tasks.py:21-28` — imports `Injury` model that is missing from `apps/api/app/models.py`.
- `apps/api/app/models.py:1` — file not formatted with `black` per project style.
