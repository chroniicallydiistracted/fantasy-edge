# CODE AUDIT & REMEDIATION — Fantasy Edge (Production-Ready, No Weather, No Fly.io)

**Use this exactly.** Perform a full audit and produce copy-ready fixes to make the **Fantasy Edge** fantasy-football dashboard production-ready.

## 0) Project Context (Authoritative)

* **Product:** Fantasy Edge — roster ingest from Yahoo, exact league-rule scoring, start/sit optimization, waivers/streamers, near-live **GameDay** (SSE deltas + optional play ticker).
* **Monorepo (expected):**

  * `apps/web` — Next.js 14 (App Router, TypeScript), deployed on **Vercel**.
  * `apps/api` — FastAPI (Python 3.11), deployed on **Render**.
  * `packages/scoring` — Python scoring / projection helpers.
  * `services/worker` (optional) — Celery jobs on **Render** (same Postgres/Redis).
  * `infra/` — Dockerfiles, `render.yaml`, CI. **No `fly.toml`.**
* **Infra (current):** Web: **Vercel** (`misfits.westfam.media`). API/Worker: **Render** (`api.misfits.westfam.media`). **Database:** Neon Postgres. **Cache/PubSub:** Upstash Redis.
* **Auth:** Yahoo OAuth (`fspt-r` now; `fspt-w` optional later). Tokens encrypted at rest.
* **Live:** SSE endpoint `/live/subscribe` backed by server-side pollers and Redis pub/sub.
* **Strict exclusions:** No Fly.io usage.

## 1) Absolute Deliverables (produce all)

**A. Findings.md** — enumerated issues with tags **Severity** `{Blocker|Major|Minor}` and **Area** `{Web|API|Worker|DB|Cache|Auth|CI|Infra}`.
**B. Incorrect-or-Incomplete.md** — explicit list of anything **wrong/misconfigured/missing/stubbed**, with **file paths and exact line ranges**.
**C. Fixes.patchset** — copy-ready unified diffs (or full file replacements) for every issue, including Fly.io removals and stack-correct replacements.
**D. PR-Plan.md** — sequenced small PRs (scope, risk, test plan, acceptance checks) ordered to reach production readiness.

> Every finding must cite concrete evidence: `path:line-start–line-end` and a one-sentence factual reason.

## 2) Mandatory Stack Corrections

**Purge Fly.io:** search `fly\.toml|flyctl|fly\.io|FLY_` (regex). Delete artifacts, scripts, envs, docs. Replace with **Render** equivalents (`render.yaml`, health checks, deploy steps). Provide exact file diffs.

## 3) Canonical Environment (use these names)

**Web (Vercel):**

* `NEXT_PUBLIC_API_BASE=https://api.misfits.westfam.media`

**API/Worker (Render):**

* `DATABASE_URL=postgresql://USER:PASS@HOST/DB?sslmode=require`  *(Neon)*
* `REDIS_URL=rediss://:PASSWORD@HOST:PORT`  *(Upstash with TLS)*
* `YAHOO_CLIENT_ID=...`
* `YAHOO_CLIENT_SECRET=...`
* `YAHOO_REDIRECT_URI=https://api.misfits.westfam.media/auth/yahoo/callback`
* `JWT_SECRET=...` *(≥32 chars)*
* `TOKEN_CRYPTO_KEY=...` *(32-byte key)*
* `LIVE_PROVIDER=yahoo|espn|manual` *(default `yahoo`)*
* `LIVE_POLL_BOX_MS=8000`
* `LIVE_POLL_PBP_MS=8000`
* `LIVE_POLL_SCOREBOARD_MS=30000`
* `LIVE_BURST_MS=4000`
* `LIVE_IDLE_TIMEOUT_MS=600000`
* `CORS_ORIGINS=https://misfits.westfam.media`

> If Upstash REST vars (`UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`) are used, either normalize to `REDIS_URL` or add a small adapter and document it in Findings.md.

## 4) Scope of Review (explicit checks you must perform)

### 4.1 Repo Hygiene & Structure

* Monorepo matches layout; no orphaned/unused packages; consistent TS/ESLint/Prettier in `apps/web`; ruff/black/mypy/pytest present for Python parts.
* Root and workspace scripts build and test deterministically; lockfiles present and valid.

### 4.2 Web (Next.js 14, Vercel)

* **App Router only:** no `pages/` mixed with `app/`. `next.config.mjs` is valid and minimal.
* **SSE client:** uses `EventSource` (or fetch streams) correctly; reconnection with backoff; unsubscribes on unmount.
* **React conventions:** stable keys, no hydration warnings, error/loading states in all routes, Suspense use correct (especially around `useSearchParams()`).
* **Server-only boundaries:** no provider/API calls from client components; all external fetches run server-side.
* **A11y baseline:** landmarks, labels, focus order; Next/Image safe usage.
* **Vercel build:** passes without missing types (`@types/react`, `@types/node`) or unsupported Node APIs.

### 4.3 API (FastAPI on Render)

* **Routers:** auth, Yahoo client, scoring, matchup, waivers, streamers, **SSE**.
* **SSE:** heartbeats; disconnect handling; Upstash Redis pub/sub namespace `live:{league_key}:w{week}` (or documented equivalent).
* **Yahoo OAuth:** code exchange, refresh handling, token **encryption at rest**; scopes restricted to `fspt-r`.
* **Scoring engine:** covers league settings fully (completions/incompletions, 40+ bonuses, first downs, return yards, pick-six penalty, IDP/K/DEF if present). Code and tests reflect exact rule math.
* **Provider access:** external calls cached server-side with retry/backoff; no client-origin calls accepted without server mediation.

### 4.4 Database (Neon Postgres)

* Migrations (Alembic) present and runnable end-to-end; schema includes league, rosters, scoring artifacts, and live telemetry tables if used (`game`, `live_snapshot`, `fantasy_totals`, `play_event`).
* `sslmode=require`; connection pooling appropriate for Render; safe transaction boundaries.

### 4.5 Cache / PubSub (Upstash Redis)

* TLS (`rediss`) enforced; secrets never logged; channel lifetimes and key expirations are defined; no blocking ops on request threads.

### 4.6 Env & Secrets

* `.env.example` is complete and matches code. No plaintext secrets committed. Variable names consistent across code, CI, and deploy targets. CORS configured to `https://misfits.westfam.media`.

### 4.7 CI/CD

* Web: Vercel project config (or `vercel.json`) with headers and cache where needed.
* API/Worker: `render.yaml` (Blueprint) with health checks; DB migrations applied on deploy; rollbacks clear.
* CI runs tests, type checks, linters; deploys block on red.

### 4.8 DX & Tests

* Fresh checkout: dev scripts run (`web`, `api`, optional `worker`) without manual tweaks.
* Unit tests for scoring math and SSE serialization; fixtures under `tests/`.

## 5) Mandatory Searches & Actions

1. **Fly.io** — Regex: `fly\.toml|flyctl|fly\.io|FLY_` → remove & replace with Render equivalents; update docs.
3. **Next pitfalls** — `useSearchParams\(\)` must be wrapped in Suspense where appropriate; detect any `pages/` directory.
4. **Leaky provider calls** — `apps/web` search for `fetch\(.*(espn|yahoo)`; these must be server-side only.
5. **Secrets** — search for `YAHOO_CLIENT_SECRET|JWT_SECRET|TOKEN_CRYPTO_KEY` in tracked files.

## 6) Output Template (fill precisely)

### A) Findings List

1. **\[Blocker]\[API]** `apps/api/main.py:88–131` — SSE lacks heartbeat; clients drop after idle.
2. **\[Major]\[Web]** `apps/web/app/(auth)/callback/page.tsx:1–40` — `useSearchParams()` used without Suspense.
3. …

### B) Incorrect or Incomplete Items

* `infra/fly.toml` — **Incorrect (obsolete)**. Remove; provide `infra/render.yaml`.
* `apps/web/app/gameday/page.tsx` — **Incomplete**: TODO for ticker rendering; missing tests.
* `apps/api/services/yahoo.py` — **Incorrect**: refresh\_token stored plaintext; must be encrypted.
* …

### C) Fixes & Diffs (copy-ready)

```diff
--- a/apps/web/app/(auth)/callback/page.tsx
+++ b/apps/web/app/(auth)/callback/page.tsx
@@
-export default function Callback() {
-  const p = useSearchParams();
-  // …
-}
+export default function Callback() {
+  return (
+    <Suspense fallback={<span>Authorizing…</span>}>
+      <CallbackInner />
+    </Suspense>
+  );
+}
+
+function CallbackInner() {
+  const p = useSearchParams();
+  // …
+}
```

*(Provide diffs for every finding, including removing Fly.io artifacts and adding Render/Vercel/Neon/Upstash config.)*

### D) PR Plan (sequenced)

* **PR-1:** Purge Fly.io; add `render.yaml`; README deploy steps; Render health checks.
* **PR-2:** Next 14 Suspense fix; build passes on Vercel; unit test for `(auth)/callback`.
* **PR-3:** Secrets hygiene: token encryption at rest; `.env.sample`; config loader.
* **PR-4:** SSE heartbeat + reconnect; Redis namespaces; integration test.
* **PR-5:** Guard server-only provider calls; feature flag wiring for live providers.

## 7) Constraints

* Do not introduce paid services.
* Do not reintroduce Fly.io.
* Keep Yahoo flow read-only (`fspt-r`) unless explicitly expanded; document any scope change.
* All fixes must be real, compilable patches — no pseudocode, no placeholders except `REPLACE_ME` for secrets.

## 8) Acceptance Criteria

* Comprehensive Findings across Web/API/Worker/DB/Cache/Auth/CI/Infra.
* Explicit Incorrect/Incomplete list with file paths and line spans.
* Patchset applies cleanly; builds/tests pass locally for web and api.
* All Fly.io traces removed; stack uses **Vercel + Render + Neon + Upstash** only.

---

Use this verbatim to direct the audit.
