# Findings

1. **[Blocker][Web]** `apps/web/postcss.config.js:1` — CommonJS export in an ESM package causes `pnpm build` to fail.
2. **[Major][Web]** `apps/web/lib/live.ts:3-6` — SSE client never retries or backs off, so the stream drops permanently on disconnect.
3. **[Major][API]** `apps/api/app/waivers.py` & `apps/api/app/routers/waivers.py` — duplicate module name `waivers` triggers MyPy import collisions.
4. **[Minor][API]** `apps/api/app/settings.py:5` — default `redis_url` uses non-TLS `redis://`; Upstash requires `rediss://`.
5. **[Major][Worker]** `services/worker/celery_app.py:7` — Celery broker defaults to `redis://` without TLS.
6. **[Major][CI]** `.github/workflows/ci.yml:105-119` — Web job installs with npm then runs pnpm, mixing package managers.
7. **[Minor][Web]** `apps/web/package-lock.json` and `apps/web/pnpm-lock.yaml` coexist, leading to inconsistent dependency locks.
8. **[Minor][Repo]** `package.json:1-6` — root Node dependencies appear unused, increasing maintenance overhead.
