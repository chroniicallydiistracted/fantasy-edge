# Blocking Issues — Fantasy Edge

This document lists concrete issues that will prevent the app from functioning in dev or production, with exact file references and suggested fixes.

## Blockers

- API login sets a non‑JWT cookie that the guards cannot read — FIXED
  - Evidence:
    - apps/api/app/routers/auth.py:231 — sets cookie value to a random `session_id` and stores metadata in Redis.
    - apps/api/app/deps.py:118 — `get_current_user_session` expects the cookie to be a signed JWT and calls `SessionManager.verify_token(...)`.
  - Impact: After a real Yahoo login, all endpoints guarded by `get_current_user_session` will return 401 because the cookie is not a JWT.
  - Fix: In `yahoo_callback`, replace the manual cookie write with `SessionManager.set_session_cookie(redirect, user.id)` so the cookie contains a JWT. Persisting a separate Redis session is unnecessary for the current guards.
  - Status: Implemented (apps/api/app/routers/auth.py)

- Render start command references a missing script — FIXED
  - Evidence:
    - render.yaml:18 — `startCommand: bash bin/prestart.sh`
    - apps/api/bin/prestart.sh — file does not exist (directory absent).
  - Impact: Render deploy will fail to start the API.
  - Fix: Either add `apps/api/bin/prestart.sh` (run Alembic then exec uvicorn) or change `startCommand` to `uvicorn app.main:app --host 0.0.0.0 --port $PORT` and run migrations via a Render deploy hook/job.
  - Status: Implemented (apps/api/bin/prestart.sh added; render.yaml unchanged and now valid)

- Dev docker‑compose references non‑existent Dockerfiles and env file — FIXED
  - Evidence:
    - infra/docker-compose.dev.yml:18 — `dockerfile: Dockerfile.dev` for API; only `apps/api/Dockerfile` exists.
    - infra/docker-compose.dev.yml:34 — `dockerfile: Dockerfile.dev` for worker; only `services/worker/Dockerfile` exists.
    - infra/docker-compose.dev.yml:52 — `dockerfile: Dockerfile.dev` for web; only `apps/web/Dockerfile` exists.
    - infra/docker-compose.dev.yml:14,34 — `env_file: ../.env.dev` — no such file in repo root.
  - Impact: `docker compose -f infra/docker-compose.dev.yml up --build` will fail to build or start.
  - Fix: Point to the existing `Dockerfile`s and provide a real `../.env.dev` (or inline env):
    - Change each `dockerfile: Dockerfile.dev` to `dockerfile: Dockerfile`.
    - Commit an `/.env.dev` with non‑secret local values, or remove `env_file` and pass envs explicitly.
  - Status: Implemented (infra/docker-compose.dev.yml updated; .env.dev added)

- Web SSR requests do not forward cookies to the API — FIXED
  - Evidence:
    - apps/web/lib/api.ts:9 — server components call `fetch(API_BASE + path, { credentials: "include" })`.
    - apps/web/app/leagues/page.tsx:5 — runs on the server (no "use client").
  - Impact: On Vercel, server‑side fetch won’t automatically include the browser’s `edge_session` cookie to the cross‑origin API, so authenticated pages 401 and render the error boundary.
  - Fix: In server components, forward the incoming request cookies to the API:
    - Use `import { cookies } from 'next/headers'` and set `headers: { cookie: cookies().toString() }` on fetch; or add Next API routes as a same‑origin proxy.
  - Status: Implemented (apps/web/lib/api.ts now forwards cookies on server)

- Hardcoded login URL bypasses `NEXT_PUBLIC_API_BASE` — FIXED
  - Evidence:
    - apps/web/app/page.tsx:9
    - apps/web/app/login/page.tsx:7
  - Impact: Local/dev/staging cannot use the correct API base; clicking login sends users to production API.
  - Fix: Build the URL from `process.env.NEXT_PUBLIC_API_BASE`.
  - Status: Implemented (apps/web/app/page.tsx and apps/web/app/login/page.tsx)

## High/Medium Risk (may not hard‑fail immediately)

- SSE auth and parameters mismatch between web and API — FIXED
  - Evidence:
    - apps/api/app/routers/live.py:16 — depends on `get_current_user` (Authorization bearer token), not cookie.
    - apps/web/lib/live.ts:8 — opens `${API_BASE}/live/subscribe` with no `league_key`/`week` query params and no Authorization.
  - Impact: If/when used, SSE will fail authorization or 422 for missing params.
  - Fix: Either switch the SSE route to `get_current_user_session` (cookie) or pass `Authorization: Bearer <JWT>` from the client, and include required `league_key` and `week` params.
  - Status: Implemented (API uses cookie guard; web client passes league/week and withCredentials)

- Duplicate route: `/team/{team_id}/waivers` — FIXED
  - Evidence:
    - apps/api/app/routers/waivers.py:12
    - apps/api/app/routers/team.py:56
  - Impact: Two identical GET routes can cause ambiguity; only one will match depending on include order.
  - Fix: Remove the duplicate from `team.py` and keep the dedicated `waivers.py` endpoint.
  - Status: Implemented (duplicate removed from apps/api/app/routers/team.py)

- Streamers page expects fields the API doesn’t return — FIXED
  - Evidence:
    - apps/web/app/l/[leagueId]/streamers/[week]/page.tsx:21 — renders `s.rank` and `s.name`.
    - apps/api/app/routers/streamers.py:33 — returns `{ player_id, projected_points }` only.
  - Impact: UI shows `undefined` fields or crashes if strict rendering assumed.
  - Fix: Include `rank`/`name` in API response or adjust the UI to display available fields.
  - Status: Implemented (apps/api/app/routers/streamers.py returns name and rank)

- SSR auth across subdomains requires cookie domain — ACTION REQUIRED
  - Evidence:
    - apps/web uses server components calling the API from `misfits.westfam.media`.
    - API sets cookie on its own host unless a cookie domain is specified.
  - Impact: In production, SSR won’t see the API cookie unless the cookie domain is set to a parent domain.
  - Fix: Set `SESSION_COOKIE_DOMAIN=.westfam.media` in Render env so the cookie is sent to both subdomains.

## Security (doesn’t block boot, but critical)

- Committed secrets in `apps/api/.env` — MITIGATED (ROTATE SECRETS OUT-OF-BAND)
  - Evidence:
    - apps/api/.env — contains live‑looking `DATABASE_URL`, `REDIS_URL`, `YAHOO_CLIENT_*`, `JWT_SECRET`, `TOKEN_CRYPTO_KEY`.
  - Impact: Key leakage risk; providers may revoke, breaking auth or data access.
  - Fix: Remove this file from git, rotate all credentials, and rely on environment injection (Render/Vercel). Keep only `.env.example` in the repo.
  - Status: File removed from repo; .gitignore already ignores .env. ACTION REQUIRED: Rotate Neon, Upstash, Yahoo, and JWT/crypto keys.

## Notes on existing Findings

- Root Findings.md claims several fixes (SSE heartbeat, typed models, cookie name) — those are present. However, new regressions were introduced:
  - `auth.py` switched to a Redis‑backed opaque session cookie incompatible with the existing cookie‑based guards.
  - Dev compose and Render start commands don’t reflect the actual files in the repo.
