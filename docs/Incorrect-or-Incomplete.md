# Incorrect or Incomplete Items

- Credentials were committed in `apps/api/.env` (now removed). All values must be rotated in providers (Neon, Upstash, Yahoo), and new secrets injected via deploy envs.
- `render.yaml` previously set a non-canonical cookie name (`fe_session`). Updated to `edge_session` to match spec; verify Render env reflects this.
- Optional for SSR across subdomains: set `SESSION_COOKIE_DOMAIN=.westfam.media` in Render to allow the web (misfits.westfam.media) to forward API cookies server-side.
- Web SSR now forwards cookies to the API. Ensure Vercel project runs on Node 20.x (as configured) so `next/headers` is available in server components.
- Local dev docker-compose switched to `npm install`. If you prefer `pnpm`, you can install pnpm in the web image and change the command; current setup favors simplicity.
