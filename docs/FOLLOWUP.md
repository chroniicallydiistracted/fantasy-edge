# Follow-Up Tasks

Date: 2025-09-01

## Items Requiring Attention
1. **Timezone Handling**
   - Replace all uses of `datetime.utcnow()` with `datetime.now(datetime.UTC)` across the API and tests to remove deprecation warnings.
2. **Projection Pipeline Integration**
   - Wire the `projections` package into worker tasks and expose projection data through API endpoints.
   - Persist generated projections in the database.
3. **Lineup Optimization (Phase 8)**
   - Implement optimization algorithms and corresponding API routes.
4. **Waivers & Streamers (Phase 9)**
   - Develop ranking logic and exposure endpoints.
5. **Frontend Expansion (Phase 10)**
   - Flesh out Next.js pages beyond the league stub and add client-side tests.
6. **Scheduling & Security (Phases 11–12)**
   - Add task scheduling with configurable intervals and implement logging/backoff/security hardening.
7. **Docs & Deployment Config (Phase 13)**
   - Author comprehensive README, provide Postman/Thunder collections, and add deployment templates.
8. **Web Testing Script**
   - Add `npm test` or equivalent for the web app, or update docs to describe testing approach.

## Signature
Reviewed by ChatGPT on 2025-09-01
