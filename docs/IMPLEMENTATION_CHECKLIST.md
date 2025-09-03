# SPEC3 Fantasy Edge Script Guide Implementation Checklist

## Database Schema and Migrations

### Authentication and User Management
- [x] 001_initial_auth - users, sessions, yahoo_accounts tables
- [x] 002_domain_core - leagues, teams, players tables
- [x] 003_roster_and_matchups - roster_slots, matchups tables
- [x] 004_projections - projections table
- [x] 005_constraints_indexes - proper constraints and indexes
- [x] 006_waivers_streamers - waiver_candidates, streamer_signals tables
- [x] 007_preferences_notes_events - user_preferences, notes, event_log tables
- [x] 008_jobs - jobs and job_runs tables for background processing

### Database Extensions
- [x] CREATE EXTENSION IF NOT EXISTS citext;
- [x] updated_at trigger function

## Redis Implementation
- [x] Session storage in Redis
- [x] OAuth PKCE/state storage in Redis
- [x] Rate limiting in Redis

## Operational Scripts
- [x] scripts/prestart.sh - Validate environment and run migrations
- [x] scripts/seed_dev.sql - Optional dev data seeding
- [x] scripts/yahoo_sync.py - Yahoo data synchronization
- [x] scripts/check_schema.sql - Schema validation

## API Endpoints
- [x] GET /me - Current user
- [x] GET /auth/yahoo/login - Yahoo OAuth login
- [x] GET /auth/yahoo/callback - OAuth callback
- [x] POST /auth/logout - Logout
- [x] GET /leagues - User leagues
- [x] GET /leagues/{leagueId}/teams - Teams in league
- [x] GET /team/{id}/roster?week= - Roster slots
- [x] GET /team/{id}/matchup?week= - Matchup
- [x] GET /players/{id}/projection?week= - Projections
- [x] GET /team/{id}/waivers?week= - Waiver candidates
- [x] GET /streamers/{kind}?week= - Streamer signals
- [x] GET /events?since= - Event log
- [x] GET/PUT /user/preferences - User preferences

## Security Implementation
- [x] PKCE implementation
- [x] State validation
- [x] Token encryption
- [x] Proper cookie configuration
- [x] CORS configuration
