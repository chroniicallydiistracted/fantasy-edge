set -euo pipefail

# Resolve to apps/api directory no matter where we’re invoked from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$APP_DIR"

# Safely extend PYTHONPATH even if it’s currently unset
export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$APP_DIR"

# Required envs (fail fast with a clear message)
: "${DATABASE_URL:?DATABASE_URL is required (use postgresql+psycopg://...)}"
: "${PORT:=8000}"

echo "[prestart] PYTHONPATH=$PYTHONPATH"

python - <<'PY'
import os, re, urllib.parse, socket
u = os.environ.get("DATABASE_URL","")
print("[prestart] DATABASE_URL =", re.sub(r':[^:@]*@', ':***@', u))
host = urllib.parse.urlparse(u).hostname
print("[prestart] HOST repr   =", repr(host))
try:
    ai = socket.getaddrinfo(host, 5432)[:1]
    print("[prestart] DNS        =", ai)
except Exception as e:
    print("[prestart] DNS_ERR    =", repr(e))
PY

echo "[prestart] Running Alembic migrations..."
alembic upgrade head

echo "[prestart] Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
