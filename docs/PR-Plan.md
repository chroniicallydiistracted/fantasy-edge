# PR Plan

1. **Switch sample Redis URLs to TLS**
   - Scope: update `apps/api/.env.example` and `services/worker/.env.example` to use `rediss://` and document the Upstash format.
   - Test Plan: `docker compose -f infra/docker-compose.dev.yml up` to verify API and worker connect using TLS URLs.
   - Acceptance: Environment samples reflect TLS scheme and services boot without errors.

2. **Document local Redis usage**
   - Scope: clarify in README that production uses `rediss://` while local development uses `redis://` via Docker.
   - Test Plan: follow README setup on a fresh clone to ensure no confusion for developers.
   - Acceptance: Developers understand when to use TLS vs non-TLS URLs.
