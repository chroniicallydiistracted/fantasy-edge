# Findings

1. **[Blocker][API]** `apps/api/app/main.py:20-26` — No SSE `/live` router implemented; live updates cannot stream to clients.
2. **[Minor][Infra]** `render.yaml:12-28` — `CORS_ORIGINS` environment variable missing; cross-origin configuration is incomplete.
3. **[Minor][Web]** `apps/web/app/login/page.tsx:7-8` — Uses `window.location.href` for navigation, causing a full page reload instead of Next.js routing.
