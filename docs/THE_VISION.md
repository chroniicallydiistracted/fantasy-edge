THE_VISION — Fantasy Edge

A fast, explainable, and delightful fantasy football companion that gives you a real competitive edge. Built as a privacy‑respecting, low‑cost hobby app that scales smoothly on Sundays.

⸻

1) One‑liner & Scope

Fantasy Edge is a web app for league managers that:
	•	Reads your Yahoo league data via OAuth (read scope by default),
	•	Computes projections and exact fantasy scoring with your custom league rules,
	•	Optimizes start/sit and waivers with clear explanations,
	•	Streams a GameDay live view (near‑live totals + optional play ticker),
	•	And (optionally) writes lineup/transactions back to Yahoo when you enable write scope.

Non‑goals: becoming a stat provider, scraping, or replacing Yahoo. Edge is a companion and analytics layer.

⸻

2) Product Pillars
	•	Speed: pages render in <2.5s on warm cache; live deltas arrive in ≤3–20s depending on provider.
	•	Explainability: every number is inspectable—show source, freshness, and formula.
	•	Reliability: graceful fallbacks; live never hard‑fails. Clear banners when degraded.
	•	Delight: small moments of joy (slot flashers, swingometer), never at the expense of clarity.

⸻

3) Personas & Primary Journeys
	•	League Manager (you & buds): connect Yahoo → see matchup hub → run optimizer → check waivers → watch GameDay → celebrate/dread with live swings.
	•	Guest Viewer (optional): view‑only links to a single matchup/GameDay.
	•	Operator (optional): manual event console to fill play text if live feed is degraded.

⸻

4) Capabilities Matrix

Capability	Status	Source(s)	Notes
Yahoo OAuth login	✅	Yahoo	fspt‑r by default; fspt‑w optional later
League ingest (settings/rosters/matchups)	✅	Yahoo	Persist raw scoring JSON for parity
Scoring engine (custom rules incl. 1D, 40+, returns, pick‑six)	✅	Local	Unit‑tested with golden cases
Projections (weekly)	✅	NFLVerse + models	Weather (NWS) adjustment
Lineup optimizer (CP‑SAT)	✅	Local	Explanations & near‑optimal alts
Waiver shortlist & FAAB bands	✅	Local + NFLVerse	ΔxFP vs worst starter
Streamers (DEF/IDP)	✅	NFLVerse	Opponent fit + pace/pressure
GameDay near‑live totals (Yahoo/Boxscore path)	✅	Yahoo/Adapter	SSE deltas
GameDay play ticker (feature‑flag)	⚙️	ESPN‑style adapter	Server‑side, cached
Manual play console & reconciliation	⚙️	Local	Never go dark
Write actions (start/sit, add/drop, trades)	🔒	Yahoo (fspt‑w)	Optional, guarded
Notifications (injuries/weather/locks)	✅	NFLVerse + NWS	Bell center + alerts

Legend: ✅ implemented/planned in SPECs; ⚙️ behind feature‑flag; 🔒 optional write mode.

⸻

5) Architecture (Prod)
	•	Web (Next.js 14, TS) at https://misfits.westfam.media (Vercel). App Router, server components, light client state.
	•	API (FastAPI, Python 3.11) at https://api.misfits.westfam.media (Render). Auth, ingest, scoring, optimizer, live orchestrator.
	•	DB: Postgres (Neon) for durable data.
	•	Cache/Live: Redis (Upstash) for pub/sub and caching.
	•	Jobs: Celery worker (Render) for nightly and game‑day jobs.
	•	Static data: NFLVerse snapshots hydrated on boot and cached to DB.

@startuml
skinparam shadowing false
actor User
User --> Web: HTTPS
Web --> API: JSON/HTTPS
API --> Postgres: SQL
API --> Redis: Pub/Sub (live)
Worker --> API: internal HTTP
Worker --> Postgres: SQL
API <- NFLVerse: batch pulls (cron)
API <- Yahoo: OAuth + league reads
API <- NWS: forecast pulls
@enduml


⸻

6) Data Sources & Contracts
	•	Yahoo Fantasy API — league/settings/rosters/matchups; tokens stored encrypted, auto‑refresh.
	•	NFLVerse — historical PBP, schedules, rosters, ID crosswalks; authoritative IDs.
	•	NWS — weather by stadium; WAF chip with timestamp.
	•	Optional ESPN‑style live adapter — scoreboard/boxscore/plays; server‑side only, cached 5–10s, feature‑flag.

Environment (prod, canonical):
	•	Web: NEXT_PUBLIC_API_BASE=https://api.misfits.westfam.media
	•	API: DATABASE_URL, REDIS_URL, YAHOO_CLIENT_ID, YAHOO_CLIENT_SECRET, YAHOO_REDIRECT_URI=https://api.misfits.westfam.media/auth/yahoo/callback, JWT_SECRET, TOKEN_CRYPTO_KEY, NWS_USER_AGENT, LIVE_PROVIDER=yahoo|espn|manual, polling intervals.

⸻

7) Security, Privacy, & ToS
	•	Store OAuth refresh tokens encrypted with TOKEN_CRYPTO_KEY; rotate keys annually.
	•	Scopes: start with fspt‑r. Only request fspt‑w when write features are enabled in settings.
	•	Strict CORS: allow only https://misfits.westfam.media.
	•	No scraping in browsers. All third‑party calls server‑side with caching/backoff; respect robots/ToS.
	•	Access logs redact user identifiers and tokens; structured JSON logging.

⸻

8) Operations & Runbooks

Preseason
	•	Seed NFLVerse IDs & schedules.
	•	Link Yahoo account; ingest league; verify scoring parity.

Weekly
	•	Tue AM: recompute projections post‑MNF; create waiver shortlist.
	•	Thu–Mon: refresh injuries & weather every few hours.

Game Day (Sun)
	•	90m pre‑kick: run final projections; warm caches; start live orchestrator.
	•	In‑game: SSE up, poll per provider cadence; degrade to near‑live if needed; keep Redis hot.
	•	Post‑game: finalize snapshots; reconcile manual events; archive week.

Incident playbook
	•	Provider 429/5xx → backoff + banner; auto‑switch to Yahoo near‑live deltas.
	•	SSE disconnect storm → lower event cadence; serve cached snapshots; auto‑reconnect.

⸻

9) UX Overview (Pages)
	•	/login — Yahoo connect.
	•	/leagues — pick league; quick health indicators.
	•	/l/{leagueId} — dashboard hub: projections, lineup optimizer, risk badges.
	•	/l/{leagueId}/waivers/{week} — waiver shortlist + FAAB bands + contingency.
	•	/l/{leagueId}/streamers/{week} — DEF/IDP streamers.
	•	/l/{leagueId}/gameday/{week} — live: top strip, drive bar, timeline, ticker, Bench Watch.
	•	/settings — feature flags, saved views, notification prefs, write‑mode toggle (🔒).

Design system: Tailwind + shadcn/ui; TanStack Table; Recharts; Zustand for live UI state; a11y AA.

⸻

10) Performance Targets
	•	Web TTI < 2.5s warm; LCP < 2.2s; CLS < 0.1.
	•	SSE reconnect < 2s; ≤10 events/sec per client; heartbeat 15s.
	•	API p95 < 300ms for read endpoints; live pollers within budgeted cadence.

⸻

11) Cost Guardrails (hobby budget)
	•	Neon/Upstash/Vercel/Render free tiers where possible.
	•	Live polling only for games with rostered players.
	•	Feature flag to disable enriched play feed if it threatens quotas.
	•	Budget alert: turn down polling to 15–30s if approaching limits.

⸻

12) Write Capabilities (Optional, 🔒)
	•	Lineup edit (start/sit) for your own team.
	•	Add/Drop & Waiver claims with FAAB slider.
	•	Propose Trade with notes and validation.
	•	Strict guardrails: scope fspt‑w, team ownership checks, lock/waiver rule checks, confirmation dialogs, and undo when supported.

⸻

13) Definition of Done (DoD)
	•	Numbers match Yahoo official totals within ±0.1 pts.
	•	Each surface has InfoTips explaining sources & formulas.
	•	A11y audits pass (Lighthouse ≥ 90).
	•	Feature flags toggle without redeploy.
	•	Incident runbooks tested in staging.

⸻

14) Master Checklists

A) Infrastructure & Domains
	•	Cloudflare DNS: misfits.westfam.media → Vercel (web) with proxied CNAME
	•	Cloudflare DNS: api.misfits.westfam.media → Render (API) with proxied CNAME
	•	Vercel project created and linked to repo; production domain added (no www)
	•	Render services created: api (FastAPI) and worker (Celery) with health checks
	•	Neon Postgres project + database created; connection pooling enabled; automatic daily backups on
	•	Upstash Redis database created (Regions: close to Render); TLS required
	•	HTTPS certs issued (Vercel & Render); HSTS enabled at Cloudflare (Strict‑Transport‑Security)
	•	Environment variables injected in Vercel (web) and Render (api/worker)
	•	CORS restricted to https://misfits.westfam.media
	•	Observability endpoints exposed: /healthz, /livez, /readyz
	•	Cache headers set for static assets (Vercel) and disabled for live endpoints
	•	Backup & restore procedure documented (Neon branch or logical backup)

B) Auth & Accounts
	•	Yahoo application created with callback https://api.misfits.westfam.media/auth/yahoo/callback
	•	Scopes requested: fspt-r (default); plan for fspt-w in write mode
	•	Token crypto configured: TOKEN_CRYPTO_KEY set; envelope encryption for refresh tokens
	•	OAuth code exchange implemented (Authlib); refresh flow scheduled via background task
	•	User table stores Yahoo identity (guid/email) and league memberships
	•	Session cookie settings: Secure, HttpOnly, SameSite=Lax (or None if cross‑site)
	•	Logout & revoke workflow (clears session + optional Yahoo revoke)
	•	Route guards on API & web pages (redirect unauthenticated users)

C) Data Ingest
	•	Ingest league settings and persist raw scoring_json verbatim
	•	Ingest teams, rosters by week, and matchups; upsert with idempotent jobs
	•	Seed NFLVerse player‑id crosswalk (espn_id, yahoo_id, gsis_id, pfr_id) weekly
	•	Map NFL teams ↔ stadiums with coordinates for weather lookup
	•	NWS station discovery per stadium; cache gridpoints and forecast responses with timestamps
	•	Injuries feed (nflreadr/nflverse) scheduled twice daily; upsert status history
	•	Projections baselines pulled (nflverse aggregates); stored for model features
	•	Data integrity checks: duplicate ids, missing positions, team mismatches
	•	Retry/backoff policy for providers; audit table for failed pulls

D) Scoring & Projections
	•	Implement offense/K/DEF/IDP scoring including bonuses: 1st downs, 40+ plays, thresholds, pick‑six penalty
	•	Golden unit tests for edge cases (e.g., 500‑yd bonus, blocked kick scoring)
	•	Store per‑player by_category breakdown with totals
	•	Weather Adjustment Factor (WAF) applied with explicit timestamp
	•	Weekly projection estimators for QB/RB/WR/TE/K/DEF/IDP
	•	Volatility band (P10/P90) computed per player
	•	Backtest: compare Week‑level projections vs actuals; log MAPE/RMSE
	•	Nightly recompute schedule and game‑day refresh cadence defined

E) Optimizer & Decisions
	•	OR‑Tools CP‑SAT lineup model with slot eligibility and one‑use constraints
	•	Diff view: highlight swaps and net delta; near‑optimal alternatives generated
	•	Waiver shortlist ranked by ΔxFP vs worst starter (position‑aware)
	•	FAAB bands heuristic + presets; configurable in settings
	•	Streamer Fit Score (DEF/IDP) including opponent pace/PROE/pressure and weather chip
	•	CSV export for waivers/shortlist; schema documented
	•	Rate‑limit and debounce optimizer calls from UI

F) GameDay (SPEC‑03)
	•	SSE endpoint /live/subscribe?league_key&week with gzip + heartbeat
	•	Redis pub/sub channel per league/week (e.g., live:2025.l.528886:w1)
	•	Live orchestrator selects only games with rostered players; cadence per game state
	•	Yahoo near‑live path stable: box/totals → scoring → delta
	•	ESPN‑style enrichment behind LIVE_PROVIDER=espn: status + play events
	•	Manual operator console routes and event storage; reconciliation job post‑game
	•	Payload validation for status, delta, play, banner; no double‑counting
	•	Client auto‑reconnect & freshness pill (LIVE/NEAR‑LIVE)

G) Web UX
	•	Routes implemented: dashboard, waivers, streamers, GameDay, settings
	•	Global nav with league picker, week selector, notifications bell
	•	Lineup DnD board with keyboard accessibility (@dnd‑kit)
	•	InfoTips on all derived numbers (formula + source + freshness)
	•	Theme (system/light/dark) persisted per user; respects prefers‑color‑scheme
	•	Mobile layouts: bottom ticker sheet + swipeable tabs on GameDay
	•	Saved views & pinned players persisted via /preferences
	•	Lighthouse a11y ≥ 90; keyboard traversal verified

H) Notifications
	•	event_log table for injuries, weather, role changes, locks, refresh events
	•	Ingestion jobs produce normalized events with league/week context
	•	Notifications drawer UI with unread badges and filters
	•	Deep links from notifications to Player/Matchup/Streamers views
	•	Deduplication + rate limiting to prevent spam
	•	Optional Discord webhook integration with opt‑in per user

I) Write Mode (🔒 Optional)
	•	Yahoo app with fspt-w scope (separate or upgraded) configured in prod
	•	Feature flag gates UI and API (WRITE_ENABLED, WRITE_LINEUP, WRITE_TRANSACTIONS, WRITE_TRADES)
	•	Permission checks: only act on the authenticated user’s team_key
	•	Lineup edit flow with pre‑submit validation (lock/position rules)
	•	Add/Drop & FAAB claim flow with waiver window/FA status checks
	•	Propose trade flow with review status surfaced
	•	Action audit log and error surfacing from Yahoo responses

J) Observability & Ops
	•	Structured JSON logging with request_id, event_id, and user id hash
	•	Metrics dashboard: poll latency, provider error rates, SSE client count
	•	Error tracking (Sentry or equivalent) wired for web and api
	•	Synthetic uptime checks for web and API health endpoints
	•	Backup/restore runbook tested quarterly (Neon + Redis snapshot)
	•	Incident runbooks: provider 429/5xx, SSE storms, quota exhaustion

K) Performance & Cost
	•	LCP/TTI/CLS budgets measured in CI and prod; regressions fail CI
	•	Code‑split charts; lazy‑render offscreen content; table virtualization
	•	Polling cadence auto‑tunes (burst mode in 2‑minute warning/OT)
	•	Cache TTLs tuned per provider; ETag/If‑Modified‑Since honored server‑side
	•	Free‑tier usage dashboards + budget alerts; feature flags to throttle

L) Docs & Onboarding
	•	/docs/SPECs.md consolidated and linked from README
	•	THE_VISION.md maintained as living doc
	•	First‑run wizard: connect Yahoo → select league → initial sync → success screen
	•	README.md quickstart + deployment steps
	•	.env.sample files for dev/stage/prod with descriptions
	•	CHANGELOG and semantic versioning policy

⸻

15) Feature‑Level Checklists

Matchup Dashboard
	•	Projected vs Opponent with spark bars and lead delta
	•	Slot cards with risk badges (injury/weather/role) and lock timers
	•	Category Waterfall chart per slot with tooltips
	•	Drag‑and‑drop lineup with slot rules (FLEX accepts WR/RB/TE)
	•	Optimize button → diffs and alternative lineups with explanations
	•	Bench Watch counter (points on bench vs optimal)
	•	InfoTips + last refresh timestamps everywhere computed

Waiver Shortlist
	•	Ranking by ΔxFP vs worst starter (position‑aware)
	•	FAAB band presets (Low/Med/High) + custom slider
	•	Acquisition probability heuristic (free‑source friendly)
	•	Quick filters (pos/team/min acquire %) and search
	•	Contingency order builder with drag/sort; CSV export
	•	(Write mode) Inline “Claim” action routes to add/drop flow

Streamers (DEF/IDP)
	•	Fit Score composed of opponent PROE/pace/pressure and recent form
	•	Weather chip (WAF) and stadium context
	•	Next‑3 opponents mini‑schedule
	•	Add‑to‑shortlist quick action; explanation modal

GameDay
	•	LIVE/NEAR‑LIVE pill with freshness timer and degrade banner
	•	Drive bar (down/distance/yard line/clock/possession)
	•	Lead timeline with zoom to drive and narration on hover
	•	Play ticker with compact narration and icons
	•	Slot flashers on player deltas; Opponent Watch toggle
	•	Optional win‑prob glidepath (feature‑flagged)

Player Modal
	•	Projection breakdown by scoring category with sources
	•	Trends charts (snaps/routes/target share) with synced tooltip
	•	Recent game log table (last 5) with efficiency notes
	•	Local notes CRUD and pin‑to‑dashboard action

Settings
	•	Feature flags (LIVE_PROVIDER, write toggles) with safe defaults
	•	Notification preferences and Discord webhook opt‑in
	•	Saved views & pins manager
	•	Manual data refresh and danger zone (unlink Yahoo)

⸻
