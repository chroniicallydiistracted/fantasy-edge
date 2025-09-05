#!/usr/bin/env bash
set -euo pipefail

# Run Alembic migrations if DATABASE_URL is set
if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "Running migrations..."
  alembic upgrade head || {
    echo "Alembic failed; continuing without migration" >&2
  }
else
  echo "DATABASE_URL not set; skipping migrations"
fi

PORT="${PORT:-8000}"
echo "Starting uvicorn on port ${PORT}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"

