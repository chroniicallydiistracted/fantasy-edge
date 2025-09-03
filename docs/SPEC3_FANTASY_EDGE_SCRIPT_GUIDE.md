# Fantasy Edge — Database Schema, Migrations & Ops Scripts (with Coding‑AI Brief)

This markdown is a **single source of truth** for the backend data model, required Alembic migrations, Redis keys, and operational scripts the Fantasy Edge stack needs. It ends with a **drop‑in prompt** for a Coding AI to implement everything safely.

> Stack assumptions: **FastAPI + SQLAlchemy + Alembic**, **Neon Postgres (public schema)**, **Upstash Redis**, **Yahoo OAuth**. Existing issues fixed here: *`roster_slots.slot` naming*, *transaction per migration*, *PKCE/state in Redis*, *Fernet encryption of tokens*.

---

## 0) Environment & Conventions

**Env vars (Render):**
- `DATABASE_URL` (e.g., `postgresql+psycopg://...`)
- `REDIS_URL` (rediss://…)
- `YAHOO_CLIENT_ID`, `YAHOO_CLIENT_SECRET`
- `YAHOO_REDIRECT_URI` → `https://api.misfits.westfam.media/auth/yahoo/callback`
- `JWT_SECRET`
- `TOKEN_CRYPTO_KEY` (Fernet 32‑byte urlsafe base64 key)
- `CORS_ORIGINS` → `https://misfits.westfam.media`
- `SESSION_COOKIE_NAME` → `fe_session`
- `SESSION_TTL_SECONDS` → `2592000` (30d)

**Global:**
- `timezone`: UTC, all timestamps `timestamptz`.
- `id` columns: `bigserial` (or `generated always as identity`) unless noted.
- Row audit: `created_at timestamptz default now()`, `updated_at timestamptz default now()`; trigger to bump `updated_at`.
- Email case‑insensitive via `citext`.

---

## 1) SQL — Tables (DDL)

> Run `CREATE EXTENSION IF NOT EXISTS citext;` once per database.

### 1.1 users
```sql
CREATE TABLE IF NOT EXISTS users (
  id               BIGSERIAL PRIMARY KEY,
  yahoo_guid       TEXT UNIQUE,                 -- Yahoo user unique guid
  email            CITEXT UNIQUE,
  display_name     TEXT,
  avatar_url       TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 1.2 sessions (server‑side web session store, cookie = `fe_session`)
```sql
CREATE TABLE IF NOT EXISTS sessions (
  id               UUID PRIMARY KEY,
  user_id          BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at       TIMESTAMPTZ NOT NULL,
  user_agent       TEXT,
  ip_addr          INET
);
CREATE INDEX IF NOT EXISTS idx_sessions_user_expires ON sessions (user_id, expires_at);
```

### 1.3 yahoo_accounts (per‑user OAuth linkage + encrypted tokens)
```sql
CREATE TABLE IF NOT EXISTS yahoo_accounts (
  id               BIGSERIAL PRIMARY KEY,
  user_id          BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  yahoo_guid       TEXT NOT NULL UNIQUE,        -- belt & suspenders
  scope            TEXT,
  access_token_enc TEXT NOT NULL,              -- Fernet encrypted
  refresh_token_enc TEXT NOT NULL,             -- Fernet encrypted
  access_expires_at TIMESTAMPTZ NOT NULL,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 1.4 leagues
```sql
CREATE TABLE IF NOT EXISTS leagues (
  id               BIGSERIAL PRIMARY KEY,
  yahoo_league_id  TEXT NOT NULL UNIQUE,       -- e.g., "406.l.12345"
  season           SMALLINT NOT NULL,
  name             TEXT NOT NULL,
  scoring_type     TEXT NOT NULL,              -- "point", "headpoint" etc
  roster_positions JSONB NOT NULL DEFAULT '[]',
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 1.5 teams
```sql
CREATE TABLE IF NOT EXISTS teams (
  id               BIGSERIAL PRIMARY KEY,
  league_id        BIGINT NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
  yahoo_team_key   TEXT NOT NULL,
  name             TEXT NOT NULL,
  logo_url         TEXT,
  manager_user_id  BIGINT REFERENCES users(id) ON DELETE SET NULL,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (league_id, yahoo_team_key)
);
CREATE INDEX IF NOT EXISTS idx_teams_league ON teams (league_id);
```

### 1.6 players
```sql
CREATE TABLE IF NOT EXISTS players (
  id               BIGSERIAL PRIMARY KEY,
  yahoo_player_id  TEXT UNIQUE,                -- nullable for custom rows
  full_name        TEXT NOT NULL,
  position_primary TEXT,                       -- e.g., "WR", "RB"
  nfl_team         TEXT,                       -- e.g., "KC"
  bye_week         SMALLINT,
  status           TEXT,                       -- OUT, Q, IR, etc.
  meta             JSONB NOT NULL DEFAULT '{}',
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_players_pos ON players (position_primary);
```

### 1.7 roster_slots  ✅ **(standardize on `slot`)**
```sql
CREATE TABLE IF NOT EXISTS roster_slots (
  id               BIGSERIAL PRIMARY KEY,
  league_id        BIGINT NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
  team_id          BIGINT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  week             SMALLINT NOT NULL,
  slot             TEXT NOT NULL,              -- e.g., QB,RB,WR,TE,FLEX,BENCH,DEF,K,IDP
  player_id        BIGINT REFERENCES players(id) ON DELETE SET NULL,
  projected_pts    NUMERIC(6,2),
  actual_pts       NUMERIC(6,2),
  is_starter       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (team_id, week, slot)
);
CREATE INDEX IF NOT EXISTS idx_roster_slots_team_week ON roster_slots (team_id, week);
```

### 1.8 matchups (team perspective)
```sql
CREATE TABLE IF NOT EXISTS matchups (
  id               BIGSERIAL PRIMARY KEY,
  league_id        BIGINT NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
  week             SMALLINT NOT NULL,
  team_id          BIGINT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  opponent_team_id BIGINT REFERENCES teams(id) ON DELETE SET NULL,
  projected_pts    NUMERIC(7,2),
  actual_pts       NUMERIC(7,2),
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (league_id, week, team_id)
);
CREATE INDEX IF NOT EXISTS idx_matchups_league_week ON matchups (league_id, week);
```

### 1.9 projections (per player/week/source)
```sql
CREATE TABLE IF NOT EXISTS projections (
  id               BIGSERIAL PRIMARY KEY,
  player_id        BIGINT NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  week             SMALLINT NOT NULL,
  source           TEXT NOT NULL,              -- "yahoo", "internal", etc.
  points           NUMERIC(6,2) NOT NULL,
  breakdown        JSONB NOT NULL DEFAULT '{}',
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (player_id, week, source)
);
CREATE INDEX IF NOT EXISTS idx_projections_week ON projections (week);
```

### 1.10 waiver_candidates
```sql
CREATE TABLE IF NOT EXISTS waiver_candidates (
  id               BIGSERIAL PRIMARY KEY,
  league_id        BIGINT NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
  week             SMALLINT NOT NULL,
  player_id        BIGINT NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  delta_xfp        NUMERIC(6,2),               -- Δ expected fantasy points vs worst starter
  fit_score        NUMERIC(5,2),
  faab_suggestion  INTEGER,
  acquisition_prob NUMERIC(5,2),
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (league_id, week, player_id)
);
```

### 1.11 streamer_signals (DEF / IDP)
```sql
CREATE TABLE IF NOT EXISTS streamer_signals (
  id               BIGSERIAL PRIMARY KEY,
  week             SMALLINT NOT NULL,
  kind             TEXT NOT NULL,              -- "def" | "idp"
  subject_id       BIGINT NOT NULL,            -- team_id for DEF; player_id for IDP
  fit_score        NUMERIC(5,2),
  weather_bucket   SMALLINT,                   -- 0..4 categorical
  meta             JSONB NOT NULL DEFAULT '{}',
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (week, kind, subject_id)
);
```

### 1.12 user_preferences
```sql
CREATE TABLE IF NOT EXISTS user_preferences (
  user_id          BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  theme            TEXT NOT NULL DEFAULT 'system',
  saved_views      JSONB NOT NULL DEFAULT '{}',
  pinned_players   BIGINT[] NOT NULL DEFAULT '{}',
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 1.13 notes (optional personal notes)
```sql
CREATE TABLE IF NOT EXISTS notes (
  id               BIGSERIAL PRIMARY KEY,
  user_id          BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  player_id        BIGINT NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  note             TEXT NOT NULL,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_notes_user_player ON notes (user_id, player_id);
```

### 1.14 event_log (notifications)
```sql
CREATE TABLE IF NOT EXISTS event_log (
  id               BIGSERIAL PRIMARY KEY,
  ts               TIMESTAMPTZ NOT NULL DEFAULT now(),
  type             TEXT NOT NULL,              -- 'injury'|'weather'|'role'|'lock'|'refresh'
  payload          JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_event_log_ts ON event_log (ts DESC);
```

### 1.15 jobs & job_runs (optional for background processing)
```sql
CREATE TABLE IF NOT EXISTS jobs (
  id               UUID PRIMARY KEY,
  kind             TEXT NOT NULL,
  payload          JSONB NOT NULL,
  not_before       TIMESTAMPTZ,
  attempts         SMALLINT NOT NULL DEFAULT 0,
  status           TEXT NOT NULL DEFAULT 'queued',
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS job_runs (
  id               BIGSERIAL PRIMARY KEY,
  job_id           UUID REFERENCES jobs(id) ON DELETE CASCADE,
  started_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at      TIMESTAMPTZ,
  ok               BOOLEAN,
  message          TEXT
);
```

---

## 2) Redis Keys (canonical)

> We store volatile, security‑sensitive, or high‑churn items in Redis.

- `session:{uuid}` → JSON `{user_id, created_at, last_seen_at}` TTL = `SESSION_TTL_SECONDS`
- `oauth:state:{state}` → JSON `{code_verifier, redirect_uri, created_at}` TTL = 600s
- `rate:ip:{route}:{ip}` → integer counter TTL = 60s
- `cache:league:{league_id}:week:{w}:summary` → presentation cache TTL = 300s

---

## 3) Alembic Migrations (idempotent, per‑migration txn)

> Configure **transaction per migration** in `alembic/env.py`:
```python
context.configure(
  connection=connection,
  target_metadata=target_metadata,
  transaction_per_migration=True,
)
```

### 3.1 001_initial_auth
- `users`, `sessions`, `yahoo_accounts`
- `citext` extension
- `updated_at` trigger function

### 3.2 002_domain_core
- `leagues`, `teams`, `players`

### 3.3 003_roster_and_matchups
- `roster_slots` (**with `slot` column name from day one**)
- `matchups`

### 3.4 004_projections
- `projections`

### 3.5 005_constraints_indexes  ✅ (fix prior break)
- `UNIQUE (team_id, week, slot)` on `roster_slots`
- supporting indexes listed above
- Use guards: only add constraints if not present.

### 3.6 006_waivers_streamers
- `waiver_candidates`, `streamer_signals`

### 3.7 007_preferences_notes_events
- `user_preferences`, `notes`, `event_log`

### Migration helper snippets
```python
from alembic import op
import sqlalchemy as sa

# Column exists helper
bind = op.get_bind()
insp = sa.inspect(bind)
cols = [c['name'] for c in insp.get_columns('roster_slots')]
if 'slot' not in cols and 'position' in cols:
    op.alter_column('roster_slots', 'position', new_column_name='slot')

# Constraint guard
exists = bind.exec_driver_sql("select 1 from pg_constraint where conname = 'uq_team_week_slot'").scalar()
if not exists:
    op.create_unique_constraint('uq_team_week_slot', 'roster_slots', ['team_id','week','slot'])
```

---

## 4) SQLAlchemy Models (high‑level)

> Mirror DDL above. Key points:
- `YahooAccount` holds *encrypted* tokens. Encryption service wraps Fernet.
- `RosterSlot.slot` is an `Enum` in Python (string in DB).
- `Session` is *not* the same as FastAPI DB session; name it `WebSession` in code.

```python
class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.BigInteger, primary_key=True)
    email = sa.Column(CIText(), unique=True)
    yahoo_guid = sa.Column(sa.Text, unique=True)
    ...

class YahooAccount(Base):
    __tablename__ = 'yahoo_accounts'
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey('users.id'), unique=True)
    access_token_enc = sa.Column(sa.Text, nullable=False)
    refresh_token_enc = sa.Column(sa.Text, nullable=False)
    access_expires_at = sa.Column(sa.DateTime(timezone=True), nullable=False)

class RosterSlot(Base):
    __tablename__ = 'roster_slots'
    team_id = sa.Column(sa.BigInteger, sa.ForeignKey('teams.id'), nullable=False)
    week = sa.Column(sa.SmallInteger, nullable=False)
    slot = sa.Column(sa.String, nullable=False)
    __table_args__ = (sa.UniqueConstraint('team_id','week','slot', name='uq_team_week_slot'),)
```

---

## 5) Auth & Security Notes

- **PKCE**: store `{state → code_verifier}` in Redis (10 min), verify exact match in callback.
- **State**: random 16–24 bytes base64url; compare in constant time.
- **Tokens**: encrypt before storing (`TokenEncryptionService(FERNET_KEY)`).
- **Cookies**: `HttpOnly; Secure; SameSite=None; Path=/; Domain=.westfam.media`.
- **CORS**: only `https://misfits.westfam.media`.

---

## 6) Operational Scripts

### 6.1 `scripts/prestart.sh` (Render)
- Validate `DATABASE_URL` and `TOKEN_CRYPTO_KEY` (masked print)
- `alembic upgrade head`
- Exec uvicorn

### 6.2 `scripts/seed_dev.sql` (optional for local/dev)
```sql
INSERT INTO users (email, display_name) VALUES ('demo@edge.local','Demo');
```

### 6.3 `scripts/yahoo_sync.py`
- Given a `user_id`, pull leagues, teams, rosters for `current_week` and upsert into `leagues`, `teams`, `players`, `roster_slots`.
- Compute `matchups` scaffolding if opponent known; otherwise leave nulls.

### 6.4 `scripts/check_schema.sql`
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY 1;
SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='uq_team_week_slot';
```

---

## 7) API Endpoints (to support current UI)

- `GET /me` → current user (via session cookie)
- `GET /auth/yahoo/login` → 302 to Yahoo (PKCE + state)
- `GET /auth/yahoo/callback` → set session cookie, redirect to web
- `POST /auth/logout` → delete server session + cookie
- `GET /leagues` → list user leagues
- `GET /leagues/{leagueId}/teams` → teams in league
- `GET /team/{id}/roster?week=` → roster_slots
- `GET /team/{id}/matchup?week=` → matchup row
- `GET /players/{id}/projection?week=` → projections
- `GET /team/{id}/waivers?week=` → waiver_candidates
- `GET /streamers/{kind}?week=` → streamer_signals
- `GET /events?since=` → event_log
- `GET/PUT /user/preferences` → user_preferences

---

## 8) Test Matrix (essentials)

- Migration 001→head on clean DB creates all tables; rerun is idempotent.
- `TokenEncryptionService` round‑trip works with `TOKEN_CRYPTO_KEY`.
- `/auth/yahoo/login` returns 302 with stored `{state, code_verifier}` in Redis.
- `/auth/yahoo/callback` rejects invalid/expired state; creates `sessions` + cookie on success.
- Constraint `uq_team_week_slot` prevents duplicate slot rows.

---

# Coding‑AI Implementation Brief

You are contributing to **apps/api** and **apps/web** in the Fantasy Edge monorepo. Implement the schema, migrations, and scripts above. Follow these rules and acceptance criteria.

## Goals
1) Create all tables and indexes as specified. 2) Make migrations **idempotent and independently transactional**. 3) Wire Redis keys for PKCE/state and sessions. 4) Keep tokens encrypted at rest. 5) Expose the minimal API surface to satisfy the current UI.

## Constraints
- Use Alembic revisions: `001_initial_auth` … `007_preferences_notes_events` matching the sections above.
- Guard every DDL with existence checks where appropriate (esp. constraints, renames).
- Ensure `roster_slots` uses **`slot`** (never `position`). If any prior code expects `position`, include a rename in 005.
- Don’t break existing prestart; keep `alembic upgrade head` as the single entrypoint.
- Ensure `alembic/env.py` has `transaction_per_migration=True`.
- Keep code that touches OAuth state/token strictly in server (no tokens to client).

## Deliverables
- New Alembic versions under `apps/api/alembic/versions/` implementing §3.
- SQLAlchemy models for tables in §4.
- Redis state/session utilities per §2.
- `scripts/yahoo_sync.py`, `scripts/check_schema.sql`, optional `scripts/seed_dev.sql`.
- Passing tests for the matrix in §8.

## Acceptance Tests
- Fresh Neon database + `alembic upgrade head` yields exactly the tables in §1.
- Re‑running `alembic upgrade head` is a no‑op (idempotent).
- `/auth/yahoo/login` → 302; Redis contains `oauth:state:{state}` with a PKCE verifier.
- `/auth/yahoo/callback` with a mocked Yahoo token exchange creates/updates `yahoo_accounts` and sets `fe_session` cookie, and `sessions` row with correct TTL.
- Insert two `roster_slots` for same `(team, week)` but different `slot` succeeds; duplicate `slot` fails.

## Pseudocode Hints
- **Encryption**
```python
class TokenEncryptionService:
    def __init__(self, key: str):
        self.fernet = Fernet(key)
    def enc(self, s: str) -> str: return self.fernet.encrypt(s.encode()).decode()
    def dec(self, s: str) -> str: return self.fernet.decrypt(s.encode()).decode()
```

- **PKCE/State**
```python
state = base64.urlsafe_b64encode(os.urandom(16)).decode().rstrip('=')
code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip('=')
redis.setex(f"oauth:state:{state}", 600, json.dumps({"code_verifier": code_verifier}))
```

- **Sessions**
```python
sid = uuid4()
redis.setex(f"session:{sid}", SESSION_TTL, json.dumps({"user_id": user.id}))
resp.set_cookie(SESSION_COOKIE_NAME, str(sid), max_age=SESSION_TTL, httponly=True, samesite="none", secure=True, domain=".westfam.media")
```

- **Upserts** (SQLAlchemy 2.0)
```python
stmt = insert(Players).values(...).on_conflict_do_update(
  index_elements=[Players.yahoo_player_id], set_={"full_name": stmt.excluded.full_name})
```

## Don’t Forget
- `CREATE EXTENSION IF NOT EXISTS citext;`
- `updated_at` trigger on all tables with that column.
- Mask secrets in logs. Keep Yahoo secrets and Fernet key out of responses.

---

**End of spec.** Commit this file as `/docs/backend-spec-db-and-scripts.md` and follow the brief to land migrations + models + scripts. 

