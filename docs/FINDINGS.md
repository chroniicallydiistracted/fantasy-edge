# Findings

Date: 2025-09-01

## Overview
The repository is a monorepo containing:
- **API** (`apps/api`) built with FastAPI and SQLAlchemy
- **Web** (`apps/web`) built with Next.js 14
- **Worker** (`services/worker`) using Celery
- **Packages** (`packages/scoring`, `packages/projections`) providing scoring utilities and projection estimators

## Completed & Production Ready
- **Phase 0 – Infra & CI Skeleton**: Docker compose, service health endpoints, `.env.example` files, and CI workflow. Tests for API, worker, scoring, and projections all pass.
- **Phase 1 – Auth Foundations**: User and OAuth token models, Fernet token encryption, JWT session cookies, debug bypass, and comprehensive tests.
- **Phase 2 – Yahoo OAuth 3-Legged Flow**: OAuth login/callback endpoints with state verification, token refresh, and user info retrieval.
- **Phase 3 – Yahoo League Read Endpoints**: Yahoo client with automatic refresh, endpoints for leagues, teams, rosters, and matchups, all covered by tests.
- **Phase 4 – Database Schema Expansion & Seeding**: Models and migrations for leagues, teams, players, injuries, weather, projections, etc., plus idempotent seeding and migration tests.
- **Phase 5 – Free Data Integrations**: Celery tasks for nflverse datasets, injury ingestion, weather forecasts, and WAF computation with caching and tests.
- **Phase 6 – Scoring Engine**: Pure scoring utilities for offense, kickers, defense, and IDP with golden tests.

## Partially Implemented
- **Phase 7 – Projection Pipeline**: Basic offensive projection estimator and worker tasks exist with tests, but the pipeline is not yet wired into the API or web layers.

## Not Started
- **Phase 8 – Lineup Optimization** and subsequent phases (Waivers, Streamers, Frontend Pages, Scheduling, Security, Docs & Deploy Config) show no implementation.

## Observations & Formatting Notes
- Multiple modules use `datetime.utcnow()`, generating deprecation warnings.
- The web app lacks a `test` script; `npm test` fails.
- Documentation is minimal; README only covers basic dev commands.

## Plan / Attack
- Replace deprecated `datetime.utcnow()` with timezone-aware calls.
- Implement remaining phases, starting with integrating the projection pipeline.
- Expand web UI, tests, and documentation.
- Add `npm test` script or clarify testing approach for the web app.

---

*Reviewed and compiled by ChatGPT on 2025-09-01*
