# Incorrect or Incomplete Items

* `apps/api/app/main.py:20-26` — Missing `/live` SSE router.
* `render.yaml:12-28` — `CORS_ORIGINS` env var absent; required for strict CORS.
* `apps/web/app/login/page.tsx:7-8` — Direct `window.location.href` navigation bypasses Next.js router.
