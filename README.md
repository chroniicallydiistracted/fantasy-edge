# Fantasy Edge

Production-ready fantasy football dashboard for Yahoo league 528886. This monorepo includes:
- FastAPI backend (`apps/api`)
- Next.js 14 web app (`apps/web`)
- Celery worker (`services/worker`)
- Scoring/optimizer/projections packages (`/packages`)

## Local Development

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
cp services/worker/.env.example services/worker/.env

# Start Postgres, Redis, API, web, and worker
docker compose -f infra/docker-compose.dev.yml up --build
# docker-compose sets REDIS_URL=redis://redis:6379/0 for local services
```

- API: http://localhost:8000/health
- Web: http://localhost:3000

## Environment Variables

### API / Worker
- `DATABASE_URL`: Postgres SQLAlchemy URL (use `?sslmode=require` for Neon)
- `REDIS_URL`: Upstash Redis (TLS in prod: `rediss://...`; local compose: `redis://redis:6379/0`)
- `JWT_SECRET`: HS256 signing key for session JWTs
- `TOKEN_CRYPTO_KEY`: 44‑char urlsafe base64 (Fernet 32‑byte key)
- `YAHOO_CLIENT_ID` / `YAHOO_CLIENT_SECRET`: Yahoo OAuth credentials
- `YAHOO_REDIRECT_URI`: OAuth callback URL
- `ALLOW_DEBUG_USER`: enable `X-Debug-User` bypass (`true|false`)
- `NWS_USER_AGENT`: contact string for `api.weather.gov`
- `CORS_ORIGINS`: comma‑separated origins (default allows `http://localhost:3000` and `https://misfits.westfam.media`)
- `SESSION_COOKIE_NAME`: defaults to `edge_session`
- `SESSION_TTL_SECONDS`: cookie/JWT TTL in seconds (default 2592000)
- `SESSION_COOKIE_DOMAIN`: optional; set to `.westfam.media` for cross‑subdomain SSR
- `LIVE_POLL_INTERVAL`: ms between live polls (default 8000)

### Web
- `NEXT_PUBLIC_API_BASE`: API base URL used by the frontend

## Testing

Python services:
```bash
cd apps/api && ruff check . && black --check . && mypy app && pytest
cd services/worker && ruff check . && black --check . && mypy tasks.py && pytest
```

Web client:
```bash
cd apps/web
pnpm lint
pnpm build
pnpm test
```

## Deployment

- Render (API): see `render.yaml` (runs `apps/api/bin/prestart.sh`, then uvicorn)
- Vercel (Web): project root directory = `apps/web`; rewrites in `infra/vercel.json`

Set all required environment variables in the respective platforms (no secrets committed).
