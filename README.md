# Fantasy Edge

A production-ready fantasy football dashboard for Yahoo league **528886**. The monorepo contains a FastAPI backend, Next.js web frontend, Celery worker, and scoring libraries.

## Local Development

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
cp services/worker/.env.example services/worker/.env

# start Postgres, Redis, API, web, and worker
docker compose -f infra/docker-compose.dev.yml up --build
# docker-compose sets REDIS_URL=redis://redis:6379/0 for local services
```

- API: http://localhost:8000/health
- Web: http://localhost:3000

## Environment Variables

### API / Worker
- `DATABASE_URL` — Postgres connection string
- `REDIS_URL` — Upstash Redis connection (use `rediss://` in production; `redis://redis:6379/0` for local Docker)
- `JWT_SECRET` — signing key for session JWTs
- `TOKEN_CRYPTO_KEY` — base64(32-byte) key for Fernet token encryption
- `YAHOO_CLIENT_ID` / `YAHOO_CLIENT_SECRET` — Yahoo OAuth credentials
- `YAHOO_REDIRECT_URI` — OAuth callback URL
- `ALLOW_DEBUG_USER` — enable `X-Debug-User` bypass (`true|false`)
- `NWS_USER_AGENT` — contact string for api.weather.gov
- `CORS_ORIGINS` — comma-separated origins (optional)

### Web
- `NEXT_PUBLIC_API_BASE` — API base URL used by the frontend

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
npm test
```

## Deployment Templates

Deployment configuration files:
- `render.yaml`
- `infra/vercel.json`

Populate service names and secrets before deploying.
