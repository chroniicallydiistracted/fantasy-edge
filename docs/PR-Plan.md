# PR Plan

1. **Implement live SSE endpoint**
   - Scope: add `/live/subscribe` router with heartbeat and register in `main.py`.
   - Test Plan: `pytest apps/api/tests/test_snapshot.py` (extend with SSE test) and `curl -N http://localhost:8000/live/subscribe` to verify heartbeats.
   - Acceptance: clients receive heartbeat events every 25s.

2. **Define CORS origins in Render config**
   - Scope: add `CORS_ORIGINS` env var in `render.yaml` matching production domain.
   - Test Plan: deploy to staging and confirm web requests succeed.
   - Acceptance: API responds with correct `Access-Control-Allow-Origin` header.

3. **Use Next.js router for Yahoo login**
   - Scope: replace `window.location.href` with `router.push` in login page.
   - Test Plan: `npm test` and manual click through login flow.
   - Acceptance: navigation happens client-side without full reload.
