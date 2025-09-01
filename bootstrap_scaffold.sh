#!/usr/bin/env bash
# SAVE AS: bootstrap_scaffold.sh
# USAGE (WSL/Ubuntu/macOS/Linux):
#   chmod +x bootstrap_scaffold.sh
#   ./bootstrap_scaffold.sh
#   cd fantasy-edge
#   cp .env.example .env
#   docker compose -f infra/docker-compose.dev.yml up --build
#
# RESULT:
#   - API at http://localhost:8000/health  -> {"ok": true}
#   - Web at http://localhost:3000
#   - Worker prints "pong"
#   - Postgres + Redis running

set -euo pipefail

root="fantasy-edge"
echo "Creating scaffold in ./$root"

# ---------- DIRECTORIES ----------
mkdir -p "$root"
mkdir -p "$root/infra"
mkdir -p "$root/apps/web/app/(auth)/callback"
mkdir -p "$root/apps/web/app/leagues"
mkdir -p "$root/apps/web/components"
mkdir -p "$root/apps/web/lib"
mkdir -p "$root/apps/web/styles"
mkdir -p "$root/apps/api/app/routers"
mkdir -p "$root/services/worker"
mkdir -p "$root/packages/scoring/scoring/tests"

# ---------- ROOT FILES ----------
cat > "$root/.env.example" <<'EOF'
# Web → API base
NEXT_PUBLIC_API_BASE=http://localhost:8000

# API
DATABASE_URL=postgresql+psycopg://ff:ff@db:5432/ff
REDIS_URL=redis://redis:6379/0
JWT_SECRET=dev-secret-change-me
NWS_USER_AGENT="Fantasy Edge Dev (contact: you@example.com)"

# Yahoo OAuth (dev)
YAHOO_CLIENT_ID=REPLACE_ME
YAHOO_CLIENT_SECRET=REPLACE_ME
YAHOO_REDIRECT_URI=http://localhost:8000/auth/yahoo/callback
EOF

cat > "$root/README.md" <<'EOF'
# Fantasy Edge (Scaffold)

## Dev quickstart
```bash
cp .env.example .env
docker compose -f infra/docker-compose.dev.yml up --build
```

- API: http://localhost:8000/health
- Web: http://localhost:3000
EOF

# ---------- INFRA ----------
cat > "$root/infra/docker-compose.dev.yml" <<'EOF'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ff
      POSTGRES_PASSWORD: ff
      POSTGRES_DB: ff
    ports: ["5432:5432"]
  redis:
    image: redis:7
    ports: ["6379:6379"]
  api:
    build: ../apps/api
    env_file: ../.env
    environment:
      DATABASE_URL: postgresql+psycopg://ff:ff@db:5432/ff
      REDIS_URL: redis://redis:6379/0
    ports: ["8000:8000"]
    depends_on: [db, redis]
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  worker:
    build: ../services/worker
    env_file: ../.env
    environment:
      REDIS_URL: redis://redis:6379/0
    depends_on: [redis]
    command: python -c "from tasks import ping; print(ping())"
  web:
    build: ../apps/web
    environment:
      NEXT_PUBLIC_API_BASE: http://localhost:8000
    ports: ["3000:3000"]
    command: npm run dev
EOF

cat > "$root/infra/vercel.json" <<'EOF'
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://api.edge.westfam.media/:path*" }
  ]
}
EOF

cat > "$root/infra/fly.api.toml" <<'EOF'
# Optional Fly.io config (not used in dev). Fill in app name later.
app = "REPLACE_ME_api"
kill_signal = "SIGINT"
kill_timeout = 5
[env]
PORT = "8000"
EOF

cat > "$root/infra/fly.worker.toml" <<'EOF'
# Optional Fly.io worker config (not used in dev). Fill in app name later.
app = "REPLACE_ME_worker"
kill_signal = "SIGINT"
kill_timeout = 5
EOF

# ---------- WEB ----------
cat > "$root/apps/web/Dockerfile" <<'EOF'
FROM node:20-alpine
WORKDIR /app
COPY package.json /app/
RUN npm install
COPY . /app
EXPOSE 3000
CMD ["npm", "run", "dev"]
EOF

cat > "$root/apps/web/package.json" <<'EOF'
{
  "name": "edge-web",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.2.5",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  },
  "devDependencies": {
    "typescript": "5.5.4",
    "tailwindcss": "3.4.10",
    "postcss": "8.4.41",
    "autoprefixer": "10.4.20"
  }
}
EOF

cat > "$root/apps/web/tsconfig.json" <<'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "baseUrl": "."
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
EOF

cat > "$root/apps/web/postcss.config.js" <<'EOF'
module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } };
EOF

cat > "$root/apps/web/tailwind.config.ts" <<'EOF'
import type { Config } from 'tailwindcss'
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: { extend: {} },
  plugins: []
}
export default config
EOF

cat > "$root/apps/web/styles/globals.css" <<'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

html, body { height: 100%; }
EOF

cat > "$root/apps/web/next.config.js" <<'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = { experimental: { serverActions: { allowedOrigins: ["*"] } } };
module.exports = nextConfig;
EOF

cat > "$root/apps/web/app/layout.tsx" <<'EOF'
import '../styles/globals.css'
import Nav from "../components/Nav"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <main className="max-w-6xl mx-auto p-6">
          <Nav />
          {children}
        </main>
      </body>
    </html>
  );
}
EOF

cat > "$root/apps/web/app/page.tsx" <<'EOF'
import Link from "next/link";
export default function Home() {
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Fantasy Edge</h1>
      <Link className="underline" href="/leagues">Go to Leagues</Link>
    </div>
  );
}
EOF

cat > "$root/apps/web/app/(auth)/callback/page.tsx" <<'EOF'
'use client'
import { useSearchParams } from 'next/navigation'
export default function Callback() {
  const sp = useSearchParams();
  return <pre>{JSON.stringify({ code: sp.get('code'), state: sp.get('state') }, null, 2)}</pre>
}
EOF

cat > "$root/apps/web/app/leagues/page.tsx" <<'EOF'
async function getLeagues() {
  const res = await fetch(process.env.NEXT_PUBLIC_API_BASE + "/yahoo/leagues", { cache: 'no-store' });
  return res.json();
}
export default async function Leagues() {
  const data = await getLeagues();
  return <pre>{JSON.stringify(data, null, 2)}</pre>;
}
EOF

cat > "$root/apps/web/components/Nav.tsx" <<'EOF'
import Link from 'next/link'
export default function Nav() {
  return (
    <nav className="flex items-center justify-between py-4">
      <Link href="/" className="font-bold">Fantasy Edge</Link>
      <div className="space-x-4">
        <Link href="/leagues" className="underline">Leagues</Link>
      </div>
    </nav>
  );
}
EOF

cat > "$root/apps/web/lib/api.ts" <<'EOF'
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
EOF

# ---------- API ----------
cat > "$root/apps/api/Dockerfile" <<'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY app /app/app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > "$root/apps/api/requirements.txt" <<'EOF'
fastapi>=0.116
uvicorn[standard]>=0.30
pydantic-settings>=2.4
sqlalchemy>=2.0
psycopg[binary]>=3.2
redis>=5.0
celery>=5.3
python-dotenv>=1.0
requests>=2.32
orjson>=3.10
numpy>=2.0
pandas>=2.2
ortools>=9.10
cryptography>=43.0
EOF

cat > "$root/apps/api/pyproject.toml" <<'EOF'
[tool.black]
line-length = 100
skip-string-normalization = true
EOF

cat > "$root/apps/api/app/settings.py" <<'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://ff:ff@db:5432/ff"
    redis_url: str = "redis://redis:6379/0"
    yahoo_client_id: str = ""
    yahoo_client_secret: str = ""
    yahoo_redirect_uri: str = "http://localhost:8000/auth/yahoo/callback"
    jwt_secret: str = "change-me"
    nws_user_agent: str = "League of Misfits Edge (contact: you@example.com)"

    class Config:
        env_file = ".env"

settings = Settings()
EOF

cat > "$root/apps/api/app/main.py" <<'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings import settings
from .routers import health, auth, yahoo, optimize

app = FastAPI(title="Fantasy Edge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://edge.westfam.media"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(yahoo.router, prefix="/yahoo", tags=["yahoo"])
app.include_router(optimize.router, prefix="/team", tags=["optimize"])
EOF

cat > "$root/apps/api/app/routers/health.py" <<'EOF'
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True}
EOF

cat > "$root/apps/api/app/routers/auth.py" <<'EOF'
import base64, os
from fastapi import APIRouter
from ..settings import settings

router = APIRouter()

AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
SCOPE = "fspt-r"

@router.get("/yahoo/login")
def yahoo_login():
    state = base64.urlsafe_b64encode(os.urandom(16)).decode()
    params = (
        f"client_id={settings.yahoo_client_id}&response_type=code&"
        f"redirect_uri={settings.yahoo_redirect_uri}&scope={SCOPE}&state={state}"
    )
    return {"redirect": f"{AUTH_URL}?{params}"}

@router.get("/yahoo/callback")
def yahoo_callback(code: str, state: str):
    # Stub: exchange handled in later step
    return {"received_code": code, "state": state}
EOF

cat > "$root/apps/api/app/routers/yahoo.py" <<'EOF'
from fastapi import APIRouter

router = APIRouter()

@router.get("/leagues")
def list_leagues():
    # Stub: will call Yahoo after OAuth is implemented
    return {"leagues": []}
EOF

cat > "$root/apps/api/app/routers/optimize.py" <<'EOF'
from fastapi import APIRouter

router = APIRouter()

@router.get("/{team_id}/optimize")
def optimize(team_id: int, week: int):
    # Stub: will call OR-Tools later
    return {"team_id": team_id, "week": week, "lineup": [], "alts": []}
EOF

cat > "$root/apps/api/app/deps.py" <<'EOF'
# Future dependency wiring (DB sessions, auth) goes here
EOF

cat > "$root/apps/api/app/models.py" <<'EOF'
# SQLAlchemy models will be added in a later step (migrations not needed to boot dev)
EOF

cat > "$root/apps/api/app/schema.sql" <<'EOF'
-- Optional: raw SQL migrations live here if needed
EOF

# ---------- WORKER ----------
cat > "$root/services/worker/Dockerfile" <<'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt || true
CMD ["python", "-c", "from tasks import ping; print(ping())"]
EOF

cat > "$root/services/worker/requirements.txt" <<'EOF'
celery>=5.3
redis>=5.0
EOF

cat > "$root/services/worker/celery_app.py" <<'EOF'
from celery import Celery
import os

BROKER = os.getenv("REDIS_URL", "redis://redis:6379/0")
BACKEND = BROKER
celery = Celery("edge", broker=BROKER, backend=BACKEND)
celery.conf.task_routes = {"tasks.*": {"queue": "default"}}
EOF

cat > "$root/services/worker/tasks.py" <<'EOF'
from .celery_app import celery

@celery.task
def ping():
    return "pong"
EOF

# ---------- SCORING PACKAGE ----------
cat > "$root/packages/scoring/pyproject.toml" <<'EOF'
[tool.pytest.ini_options]
addopts = "-q"
EOF

cat > "$root/packages/scoring/scoring/__init__.py" <<'EOF'
from .league_scoring import Statline, offense_points
EOF

cat > "$root/packages/scoring/scoring/league_scoring.py" <<'EOF'
from dataclasses import dataclass

def bonus_bins(val, bins):
    return sum(1 for b in bins if val >= b)

@dataclass
class Statline:
    Comp: float = 0; Incomp: float = 0; PassYds: float = 0; PassTD: float = 0; INT: float = 0
    PickSix: float = 0; Pass1D: float = 0; RushYds: float = 0; RushTD: float = 0; Rush1D: float = 0
    Rec: float = 0; RecYds: float = 0; RecTD: float = 0; Rec1D: float = 0
    RetYds: float = 0; RetTD: float = 0; TwoPt: float = 0; FumblesLost: float = 0; OffFumRetTD: float = 0
    e40c: float = 0; e40ptd: float = 0; e40r: float = 0; e40rtd: float = 0; e40rec: float = 0; e40rectd: float = 0

def offense_points(s: Statline) -> float:
    return (
        0.25*s.Comp - 0.25*s.Incomp + s.PassYds/25 + 2*bonus_bins(s.PassYds,[300,400,500])
        + 6*s.PassTD - 2*s.INT + 2*s.e40c + 2*s.e40ptd + 0.5*s.Pass1D - 2*s.PickSix
        + s.RushYds/10 + 2*bonus_bins(s.RushYds,[100,150,200]) + 6*s.RushTD + 2*s.e40r + 2*s.e40rtd + 0.5*s.Rush1D
        + s.Rec + s.RecYds/10 + 2*bonus_bins(s.RecYds,[100,150,200]) + 6*s.RecTD + 2*s.e40rec + 2*s.e40rectd + 0.5*s.Rec1D
        + s.RetYds/30 + 6*s.RetTD + 2*s.TwoPt - 2*s.FumblesLost + 6*s.OffFumRetTD
    )
EOF

cat > "$root/packages/scoring/scoring/tests/test_scoring.py" <<'EOF'
from scoring.league_scoring import Statline, offense_points

def test_qb_bonus_and_penalties():
    s = Statline(Comp=25, Incomp=15, PassYds=405, PassTD=3, INT=1, PickSix=1, Pass1D=12)
    pts = offense_points(s)
    expected = 0.25*25 - 0.25*15 + 405/25 + 2*2 + 6*3 - 2 - 2 + 0.5*12
    assert round(pts, 2) == round(expected, 2)
EOF

echo "✅ Scaffold created at ./$root"
echo "Next:"
echo "  cd $root"
echo "  cp .env.example .env"
echo "  docker compose -f infra/docker-compose.dev.yml up --build"
