set -euo pipefail
export PYTHONPATH="$PYTHONPATH:$(cd "$(dirname "$0")/.." && pwd)"
echo "[prestart] PYTHONPATH=$PYTHONPATH"
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"