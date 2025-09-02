# Incorrect or Incomplete Items

- `apps/web/postcss.config.js:1` — uses CommonJS `module.exports` in an ESM project; Next.js build fails.
- `apps/web/lib/live.ts:3-6` — SSE subscription lacks reconnection/backoff logic.
- `apps/api/app/waivers.py:1-40` & `apps/api/app/routers/waivers.py:1-20` — duplicate module names (`waivers`) produce MyPy error: "Duplicate module named 'waivers'".
- `apps/api/app/settings.py:5` — default `redis_url` uses `redis://` instead of required TLS `rediss://`.
- `services/worker/celery_app.py:7` — `REDIS_URL` fallback uses non-TLS `redis://redis:6379/0`.
- `.github/workflows/ci.yml:105-119` — web CI step mixes `npm ci` with `pnpm lint`/`pnpm build`.
- `apps/web/package-lock.json` vs `apps/web/pnpm-lock.yaml` — multiple lockfiles tracked.
- `package.json:1-6` — root dependencies (`dotenv`, `pg`) unused by workspace.
