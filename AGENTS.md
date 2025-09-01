# Fantasy Edge — Phased Build Plan (AI‑Ready)

**Goal:** Deliver a production‑ready Fantasy Football dashboard for Yahoo league **528886**. This plan breaks the MASTER BUILD PROMPT into executable phases with tight scopes, acceptance criteria, and copy‑paste sub‑prompts for a coding AI. Keep `/apps/web` and `/apps/api` separation, Celery in `/services/worker`, scoring in `/packages/scoring`.

> **No placeholders** except secrets/URLs explicitly marked `REPLACE_ME`.


## Repo & Infra Snapshot (canonical)

- **Frontend (Web):** Next.js 14 app in `apps/web`, deployed on **Vercel**. Production domain: **https://misfits.westfam.media**. Project Root Directory on Vercel = `apps/web`. Uses env **`NEXT_PUBLIC_API_BASE`** for all API calls.
- **Backend (API):** FastAPI app in `apps/api`, deployed on **Render (Free Web Service)**. Custom production domain: **https://api.misfits.westfam.media**; fallback during setup: **`https://<your-service>.onrender.com`**. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Health: `GET /health`.
- **Database:** **Neon Postgres**. Connect with SQLAlchemy (psycopg v3). **`DATABASE_URL`** format: `postgresql+psycopg://USER:PASSWORD@HOST:5432/DB?sslmode=require`.
- **Cache / Broker:** **Upstash Redis** (TLS). **`REDIS_URL`** format: `rediss://:PASSWORD@HOST:PORT`.
- **OAuth Provider:** **Yahoo Fantasy Sports** (scope `fspt-r`). **Redirect URIs registered:**
  - `https://api.misfits.westfam.media/auth/yahoo/callback` (custom domain)
  - `https://<your-service>.onrender.com/auth/yahoo/callback` (Render fallback)
  Optional OIDC scopes (`openid profile email`) are fine but not required.
- **DNS (Cloudflare):**
  - `misfits.westfam.media` → CNAME to Vercel target.
  - `api.misfits.westfam.media` (Name: `api.misfits`) → CNAME to Render’s provided target. Keep **DNS only** until SSL shows “Ready” in Render.
- **CORS (API):** allow origins **`https://misfits.westfam.media`** and **`http://localhost:3000`**.
- **Session Cookie:** name **`edge_session`**, `HttpOnly`; dev: `SameSite=Lax`; prod: `SameSite=None; Secure`.
- **Build/runtime:** Vercel Node **20.x**; Render Python **3.11**. No web `/callback` page — OAuth callback is handled by API at `/auth/yahoo/callback`.

### Canonical environment variables

**API (Render)**
- `DATABASE_URL` — Neon SQLAlchemy URL (`postgresql+psycopg://...?...sslmode=require`)
- `REDIS_URL` — Upstash TLS URL (`rediss://:...@host:port`)
- `JWT_SECRET` — long random string (JWT signing)
- `TOKEN_CRYPTO_KEY` — 32‑byte base64 key for Fernet token encryption
- `NWS_USER_AGENT` — e.g., `Fantasy Edge (contact: you@example.com)`
- `YAHOO_CLIENT_ID` — from Yahoo Dev
- `YAHOO_CLIENT_SECRET` — from Yahoo Dev
- `YAHOO_REDIRECT_URI` — current callback in use (Render fallback or custom API domain)
- `ALLOW_DEBUG_USER` — `true|false` (dev‑only bypass header)
- `CORS_ORIGINS` (optional) — comma‑separated list, default includes the two above

**Web (Vercel Production)**
- `NEXT_PUBLIC_API_BASE` — `https://api.misfits.westfam.media` (or temporary Render URL)

**Worker (optional later)**
- `REDIS_URL` — same as API
- `DATABASE_URL` — if the worker reads/writes DB

### Live endpoints (once deployed)
- Web: `https://misfits.westfam.media`
- API (custom): `https://api.misfits.westfam.media/health`
- API (fallback): `https://<your-service>.onrender.com/health`

---

## Phase 0 — Repo Sanity, Dev Infra, CI Skeleton

**Scope**
- Validate scaffold structure. Ensure Docker dev environment brings up API, Web, Postgres, Redis, and Celery w/ hot‑reload.
- Add baseline CI: lint + type + unit tests + Docker build matrix.

**Deliverables**
- `infra/docker-compose.dev.yml` verified; healthcheck endpoints for API (`/health`) and worker (`/healthz`).
- GitHub Actions: run `ruff`/`flake8`, `black --check`, `mypy`, `pytest`, web `pnpm lint && pnpm build`, build Docker images.
- Central `.env.example` files for API, worker, and web with `REPLACE_ME` secrets.

**DoD**
- `docker compose -f infra/docker-compose.dev.yml up --build` boots; API at `http://localhost:8000/health`.
- CI green on a PR.

**Copy‑paste prompt to Coding AI**
```text
Task: Phase 0 — Infra & CI Skeleton.
Repo: use existing scaffold; do not move directories.
Implement:
1) API /health (FastAPI), Worker /healthz (FastAPI or simple HTTP via Uvicorn in worker).
2) Docker: confirm services run; expose ports: API 8000, Web 3000, Redis 6379, Postgres 5432, Worker.
3) GH Actions: Python 3.11, Node 20. Run ruff+black+mypy+pytest; pnpm lint+build; docker build for api/web/worker.
4) Add .env.example for apps/api, services/worker, apps/web with required vars (see MASTER), using REPLACE_ME for secrets.
5) Ensure CORS allows http://localhost:3000 by default.
Output: minimal code changes and CI files only; no business logic.
```

---

## Phase 1 — Auth Foundations (Users, Token Encryption, Dev Bypass)

**Scope**
- DB models/migrations for `user` and `oauth_token`.
- Symmetric encryption at rest for tokens (Fernet or libsodium).
- Dev bypass header `X-Debug-User: 1` gated by env.
- JWT session cookie issuing/verification (signed, httpOnly, SameSite=Lax in dev).

**Deliverables**
- Alembic migration creating `user(id, email, created_at)` and `oauth_token(user_id, provider, access_token, refresh_token, expires_at, scope, guid)`.
- Encryption service + key from env `TOKEN_CRYPTO_KEY`.
- `/auth/session/debug` for dev: set cookie when `X-Debug-User` is present and feature flag enabled.
- Unit tests: encryption roundtrip; cookie auth guard; bypass respects flag.

**DoD**
- Tests pass.
- Cookie appears for dev route and guards protected endpoints.

**Copy‑paste prompt**
```text
Task: Phase 1 — Auth Foundations.
Implement SQLAlchemy models + Alembic migrations for user and oauth_token.
Add token encryption service using cryptography.Fernet with key TOKEN_CRYPTO_KEY=REPLACE_ME (document length/format).
JWT session cookies: HS256 with SESSION_SECRET=REPLACE_ME. Cookie name: edge_session.
Add dependency to read session or debug header when ALLOW_DEBUG_USER=true.
Add tests for: encryption, cookie parsing, debug bypass on/off.
```

---

## Phase 2 — Yahoo OAuth 3‑Legged Flow

**Scope**
- Full Yahoo OAuth (`fspt-r` scope), token exchange/refresh, persist encrypted tokens.
- Callback issues web session cookie.

**Endpoints**
- `GET /auth/yahoo/login` → returns redirect URL with state.
- `GET /auth/yahoo/callback?code&state` → exchanges token at `https://api.login.yahoo.com/oauth2/get_token` using Basic auth (base64 client_id:client_secret); persist `access_token`, `refresh_token`, `expires_at`, `scope`, `xoauth_yahoo_guid`.

**Deliverables**
- Token refresh if within 5 min of expiry automatically.
- Error handling with backoff+jitter; secrets masked in logs.
- Tests: state checks, exchange happy/refresh paths (mock HTTP), persistence encrypted.

**DoD**
- Manual login works end‑to‑end in dev; cookie set; token stored encrypted.

**Copy‑paste prompt**
```text
Task: Phase 2 — Yahoo OAuth.
Implement /auth/yahoo/login and /auth/yahoo/callback in FastAPI.
Use envs: YAHOO_CLIENT_ID=REPLACE_ME, YAHOO_CLIENT_SECRET=REPLACE_ME, YAHOO_REDIRECT_URI=http://localhost:8000/auth/yahoo/callback.
Build token client with automatic refresh when expires_at - now < 300s.
Persist encrypted tokens tied to user row; create user on first login (email from Yahoo if available, else null).
Return a signed JWT cookie to the browser on success and redirect to apps/web /leagues.
Add unit tests with httpx mocking for token exchange + refresh.
```

---

## Phase 3 — Yahoo League Read Endpoints (Raw Pass‑Through)

**Scope**
- Implement read‑only Yahoo API wrappers and map to API endpoints.
- Minimal normalization; passthrough of raw JSON.

**Endpoints**
- `GET /yahoo/leagues`
- `GET /yahoo/league/{league_key}` (include raw league meta + normalized scoring map skeleton)
- `GET /yahoo/league/{league_key}/teams`
- `GET /yahoo/league/{league_key}/rosters?week=N`
- `GET /yahoo/league/{league_key}/matchups?week=N`

**Deliverables**
- Yahoo client w/ rate limiting, retries, and error surfaces.
- Tests: each endpoint mocked; auth guard; refresh path coverage.

**DoD**
- Able to list/select **2025.l.528886** in dev.

**Copy‑paste prompt**
```text
Task: Phase 3 — Yahoo Read Endpoints.
Implement a Yahoo API client with automatic token injection and refresh. Build endpoints:
- /yahoo/leagues
- /yahoo/league/{league_key}
- /yahoo/league/{league_key}/teams
- /yahoo/league/{league_key}/rosters?week=N
- /yahoo/league/{league_key}/matchups?week=N
Return raw JSON plus for league meta also return a normalized scoring map skeleton.
Mock Yahoo HTTP in tests; verify auth guard and refresh.
```

---

## Phase 4 — Database Schema Expansion & Seeding

**Scope**
- Create Alembic migrations for domain tables:
  - `league`, `team`, `player`, `roster_slot`, `injuries`, `weather`, `baselines`, `projections`, `recommendations`, `player_link(yahoo_key, gsis_id, pfr_id, player_id PRIMARY KEY, last_manual_override BOOLEAN DEFAULT false)`.
- Seed league id `528886` upon first sync.

**Deliverables**
- Pydantic v2 schemas; SQLAlchemy 2.x models.
- Seed script wired to Celery task or API admin endpoint.
- Tests: migration heads, FK integrity, unique constraints, and seed idempotency.

**DoD**
- `alembic upgrade head` succeeds in CI; seed completes idempotently.

**Copy‑paste prompt**
```text
Task: Phase 4 — DB Schema Expansion.
Add Alembic migrations and SQLAlchemy models for all domain tables listed in the SPEC. Implement seed pathway to insert league 528886 when absent. Add unit tests validating constraints and idempotent seeding.
```

---

## Phase 5 — Free Data Integrations (nflverse, injuries, NWS)

**Scope**
- Celery jobs to pull/store:
  - **nflverse / nflfastR**: season rosters, schedules, play‑by‑play; cache under `/data` volume; support ETag conditional requests.
  - **nflreadr injuries** → normalize to `injuries` with `report_time`.
  - **NWS** `api.weather.gov`: compute Weather Adjustment Factor (WAF) using stadium lat/lon; honor `settings.nws_user_agent` header.

**Deliverables**
- Data access layer and mappers to DB.
- Retry/backoff; respectful rate limits; local cache.
- Tests with on‑disk small fixtures; WAF unit tests.

**DoD**
- Jobs runnable locally; tables populated.

**Copy‑paste prompt**
```text
Task: Phase 5 — External Data Jobs.
Implement Celery tasks for nflverse CSV/Parquet ingest with caching+ETag, nflreadr injuries normalization, and NWS forecasts with WAF computation. Add configuration for /data volume. Provide unit tests using small local fixtures; do not call the internet in tests.
```

---

## Phase 6 — Scoring Engine (Packages)

**Scope**
- Complete `packages/scoring/scoring/league_scoring.py` to compute fantasy points for Offense, K, DEF/ST, and IDP including bonuses: 1st downs, 40+ plays, return yards, 100/150/200 and 300/400/500 thresholds, pick‑six penalties, etc.
- Exhaustive tests under `packages/scoring/scoring/tests/` with golden fixtures (3 realistic statlines per position).

**Deliverables**
- Deterministic scoring functions; clear docs.
- Golden test fixture and edge case coverage.

**DoD**
- `pytest` for scoring passes in CI.

**Copy‑paste prompt**
```text
Task: Phase 6 — Scoring Engine.
Finish league_scoring.py implementing exact rules per SPEC. Add golden tests with 3 per position and edge cases for 40+ events, first downs, return yards, bonuses, pick-sixes. Keep functions pure; no I/O.
```

---

## Phase 7 — Projection Pipeline

**Scope**
- Per‑position estimators outputting **category expectations** that the scoring engine consumes.
- Blend historical rates (nflfastR), opponent/context, and weather (WAF). Store JSON breakdowns in `projections`.

**Deliverables**
- Services with pluggable estimators; variance estimates if available.
- Tests: sanity on shapes, monotonicity under obvious changes (e.g., higher PROE → more WR targets), and weather sensitivity.

**DoD**
- `projections` populated for an example week.

**Copy‑paste prompt**
```text
Task: Phase 7 — Projection Pipeline.
Implement per-position estimators that consume nflfastR aggregates + opponent context + WAF, outputting category expectations. Persist JSON in projections table. Include variance estimate when possible. Provide unit tests for shapes and simple property-based checks.
```

---

## Phase 8 — Lineup Optimizer (CP‑SAT)

**Scope**
- OR‑Tools CP‑SAT model with slots: QB, WR×3, RB×2, TE, W/R/T (FLEX), K, DEF, DB, DL, LB; bench rest.
- Eligibility: FLEX ∈ {WR, RB, TE}. Objective maximize projected points; tie‑break on lower variance.
- Endpoint: `GET /team/{team_id}/optimize?week=N` → optimal + 3 near‑optimal alternatives with explanations (delta by categories and risk).

**Deliverables**
- Solver service; clear explanations; timeout guards.
- Tests: small synthetic rosters validate constraints, tie‑break behavior, and alternatives.

**DoD**
- Endpoint returns consistent optimal lineup on fixtures.

**Copy‑paste prompt**
```text
Task: Phase 8 — CP-SAT Lineup Optimizer.
Build OR-Tools model with exact slot/eligibility rules. Objective: maximize projected points; secondary minimize variance. Return 1 optimal + 3 near-optimal distinct lineups with category delta explanations. Add tests on synthetic data.
```

---

## Phase 9 — Waivers & Streamers

**Scope**
- Celery task `waiver_shortlist(league_key, week, horizon)` ranking **ΔxFP** vs worst starter; estimate acquisition probability from public ownership & bye fit; include contingency order.
- Streaming boards for DEF and IDP using opponent pressure allowed, pace, PROE, weather.

**Endpoints**
- `GET /team/{team_id}/waivers?week=N&horizon=2`
- `GET /streamers/def?week=N` and `/streamers/idp?week=N`

**Deliverables**
- Ranking logic; explainability fields.
- Tests on ranking monotonicity and tie handling.

**DoD**
- Endpoints return stable rankings on fixtures.

**Copy‑paste prompt**
```text
Task: Phase 9 — Waivers & Streamers.
Implement waiver_shortlist Celery task and streaming endpoints. Rank by ΔxFP vs worst starter; include acquisition probability and contingency order. Provide tests ensuring monotonicity and deterministic ties.
```

---

## Phase 10 — Frontend (Next.js 14, TS)

**Scope**
- Real UI, no placeholders. Tailwind, TanStack Table v8, Recharts.

**Pages**
- `/login` → calls `/auth/yahoo/login` and follows redirect.
- `/leagues` → lists leagues; allow select `2025.l.528886`.
- `/l/{leagueId}/matchup/{week}` → optimal lineup, opponent guessed lineup, win odds placeholder (UI reserves slot), per‑slot justifications.
- `/l/{leagueId}/waivers/{week}` → ranked waiver targets with ΔxFP and contingency.
- `/l/{leagueId}/streamers/{week}` → DEF & IDP tiles with fit scores.
- `/settings` → CSV/Google Sheets importer for manual roster bootstrap.

**Deliverables**
- API client using `NEXT_PUBLIC_API_BASE`.
- Loading, error states, and responsive layouts.
- Component tests where feasible.

**DoD**
- Pages render against dev API; tables and charts functional.

**Copy‑paste prompt**
```text
Task: Phase 10 — Next.js Frontend.
Build pages per SPEC using App Router, TS, Tailwind, TanStack Table v8, Recharts. Wire to API via NEXT_PUBLIC_API_BASE. Implement real loading/error states. No placeholders for data that the API already provides; where future services are pending, show explicit "Coming from API soon" banners with feature flags.
```

---

## Phase 11 — Jobs & Scheduling

**Scope**
- Celery Beat or APScheduler in worker:
  - Nightly data sync.
  - Tuesday morning waiver shortlist.
  - Game day projection refresh every 10 minutes from T‑90 to final.

**Deliverables**
- Schedules as code; observability logs.
- Tests: schedule config unit tests; job wiring.

**DoD**
- Schedules active in dev with compressed intervals for testing.

**Copy‑paste prompt**
```text
Task: Phase 11 — Scheduling.
Add Celery Beat schedule entries (or APScheduler) for nightly sync, waiver shortlist on Tuesday morning, and game-day 10-minute refresh windows. Make intervals configurable via envs. Provide tests validating schedule construction.
```

---

## Phase 12 — Security & Resilience

**Scope**
- Token encryption, masked logs, request backoff/jitter, Yahoo request snapshotting prior to locks.
- CORS per domain defaults.

**Deliverables**
- Central logging config; PII scrubbing; structured logs.
- Error‑budget docs and retry policy.

**DoD**
- Security checklist passes; secrets never logged.

**Copy‑paste prompt**
```text
Task: Phase 12 — Security.
Implement logging filter to mask secrets, exponential backoff with jitter on Yahoo client, snapshot last known good state before lineup locks. Verify CORS defaults and cookie security attributes. Add tests for masking filter and retry policy.
```

---

## Phase 13 — Docs, Collections, Deployment Config

**Scope**
- `README.md` with local dev steps and env var docs.
- Postman/Thunder Client collection.
- Deployment configs: `infra/fly.api.toml`, `infra/fly.worker.toml`, `infra/vercel.json` (rewrites), CORS.

**Deliverables**
- CI building Docker images.
- Smoke tests in CI that hit `/health`.

**DoD**
- One‑command dev up; docs accurate; collections importable.

**Copy‑paste prompt**
```text
Task: Phase 13 — Docs & Deploy Config.
Author README with precise local dev steps. Provide Postman/Thunder Client collection. Add Fly.io and Vercel configs per domains. Ensure CI builds images and runs a minimal smoke test.
```

---

## Cross‑Cutting Requirements

- **Env Vars (API/Worker)**
  - `JWT_SECRET` — HS256 signing key for session JWTs
  - `TOKEN_CRYPTO_KEY` — base64(32‑byte) key for Fernet encryption at rest
  - `YAHOO_CLIENT_ID`, `YAHOO_CLIENT_SECRET` — from Yahoo Dev
  - `YAHOO_REDIRECT_URI` — exact HTTPS callback used in current env
  - `NEXT_PUBLIC_API_BASE` — web → API base URL (frontend only)
  - `DATABASE_URL` — Neon SQLAlchemy URL (`postgresql+psycopg://...?...sslmode=require`)
  - `REDIS_URL` — Upstash TLS URL (`rediss://...`)
  - `ALLOW_DEBUG_USER` — `true|false` dev bypass
  - `NWS_USER_AGENT` — user agent for api.weather.gov

- **Testing Policies**
  - External HTTP mocked; fixtures checked into repo.
  - Golden tests for scoring; deterministic seeds.

- **Performance/Resilience**
  - Retries with jitter; timeouts; circuit breakers where applicable.

- **Observability**
  - Structured logs; request IDs; Celery task IDs.

---


## Phase Gates (CI Checklists)

- **P0 Gate**: Docker up; API `/health` 200; CI green.
- **P1 Gate**: Auth tests passing; dev bypass behind flag; encrypted tokens persisted.
- **P2 Gate**: Yahoo OAuth E2E; refresh covered by tests.
- **P3 Gate**: Read endpoints functional against mocks; manual league select works.
- **P4 Gate**: Migrations apply; seed idempotent.
- **P5 Gate**: Jobs run with fixtures; WAF computed.
- **P6 Gate**: Scoring tests all pass.
- **P7 Gate**: Projections populated; sanity tests pass.
- **P8 Gate**: Optimizer returns optimal + 3 alts; tests pass.
- **P9 Gate**: Waivers/streamers ranked deterministically.
- **P10 Gate**: Frontend pages functional against dev API.
- **P11 Gate**: Schedules fire in dev.
- **P12 Gate**: Security checklist ✓.
- **P13 Gate**: README/Collections present; deploy configs validated.

---

## Hand‑Off Template (Per Phase PR)

- _Summary_: what changed
- _Env changes_: new/updated envs
- _Migrations_: yes/no
- _Testing_: commands + coverage highlights
- _Manual QA_: exact steps
- _Risks_: known issues

---

## Nice‑to‑Have (Post‑MVP)
- Monte Carlo win odds engine (simulator service).
- Caching layer for hot endpoints.
- Feature flags for UI experiments.

