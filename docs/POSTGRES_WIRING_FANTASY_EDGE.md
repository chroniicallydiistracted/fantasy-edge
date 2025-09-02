**POSTGRES WIRING — FANTASY EDGE (Repo‑Exact, End‑to‑End Instructions for Coding AI)**  
  
Implement **PostgreSQL (Neon)** end‑to‑end for *this* repository only. Use the file paths and code below as the single source of truth. Do not add unrelated features. Do not change product scope. Focus purely on DB wiring (engine/session, models, migrations, envs, health check, and minimal tests).  
  
**Repo root:** fantasy-edge-main/  
  
Key paths used here:  
	•	API root: apps/api  
	•	App code: apps/api/app  
	•	Alembic: apps/api/alembic  
	•	Requirements: apps/api/requirements.txt  
	•	Tests: apps/api/tests  
  
⸻  
  
**0) Deliverables (checklist)**  
	•	Dependencies present (sqlalchemy, psycopg[binary], alembic)  
	•	Central SQLAlchemy engine/session + FastAPI get_db dependency  
	•	ORM models implemented for:  
	•	User, OAuthToken, League, Team, Player, PlayerLink, RosterSlot, Projection  
	•	Alembic configured to read env DATABASE_URL; **initial migration** creates schema  
	•	/health endpoint verifies DB connectivity via SELECT 1  
	•	.env.example shows **Neon** and local values for DATABASE_URL  
	•	Render pre‑deploy step runs alembic upgrade head  
	•	Minimal tests: SELECT 1 and a User CRUD round trip  
  
⸻  
  
**1) Dependencies (apps/api)**  
  
**Ensure these exist in** apps/api/requirements.txt:  
  
```
sqlalchemy>=2.0
psycopg[binary]>=3.2
alembic>=1.12
fastapi>=0.116
uvicorn[standard]>=0.30

```
pydantic-settings>=2.4  
  
*(Leave other entries unchanged.)*  
  
Local dev tool (optional for WSL/mac):  
  
```
sudo apt-get update && sudo apt-get install -y postgresql-client

```
  
  
⸻  
  
**2) Engine & Session (centralized)**  
  
**Edit/Create:** apps/api/app/deps.py — **replace the top‑of‑file engine/session block** with this (keep existing auth helpers below):  
  
```
# apps/api/app/deps.py — database engine/session and FastAPI dependency
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .settings import settings

# Use settings.database_url; for Neon, ensure the value ends with ?sslmode=require
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

```
  
No other changes in this file are required for DB wiring.  
  
⸻  
  
**3) ORM Models (apps/api/app/models.py)**  
  
**Replace the entire file** apps/api/app/models.py with the following complete definitions that match current routers and tests:  
  
```
# apps/api/app/models.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float, JSON,
    UniqueConstraint, Index, func
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ----------------------
# Auth & Identity
# ----------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    oauth_tokens = relationship("OAuthToken", back_populates="user", cascade="all, delete-orphan")

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String, nullable=False)  # e.g., "yahoo"
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    scope = Column(Text, nullable=True)
    guid = Column(String, unique=True, index=True)  # Yahoo GUID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    user = relationship("User", back_populates="oauth_tokens")

# ----------------------
# League & Team
# ----------------------
class League(Base):
    __tablename__ = "leagues"
    id = Column(Integer, primary_key=True)
    yahoo_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    season = Column(Integer, nullable=True)
    scoring_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, ForeignKey("leagues.id", ondelete="CASCADE"), nullable=False, index=True)
    team_key = Column(String, unique=True, nullable=True, index=True)
    name = Column(String, nullable=True)
    manager_guid = Column(String, nullable=True, index=True)
    logo_url = Column(Text, nullable=True)

# ----------------------
# Players, Links, Roster, Projections
# ----------------------
class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    position = Column(String, nullable=True, index=True)  # QB/RB/WR/TE/K/DEF/IDP
    team = Column(String, nullable=True, index=True)      # NFL team code
    status = Column(String, nullable=True)
    # relationships
    link = relationship("PlayerLink", back_populates="player", uselist=False, cascade="all, delete-orphan")

class PlayerLink(Base):
    __tablename__ = "player_links"
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), primary_key=True)
    yahoo_key = Column(String, unique=True, nullable=True, index=True)
    gsis_id = Column(String, unique=True, nullable=True, index=True)
    pfr_id = Column(String, unique=True, nullable=True, index=True)
    last_manual_override = Column(Boolean, default=False, nullable=False)
    # relationships
    player = relationship("Player", back_populates="link")

class RosterSlot(Base):
    __tablename__ = "roster_slots"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    week = Column(Integer, nullable=False, index=True)
    slot = Column(String, nullable=True)  # QB/RB/WR/TE/FLEX/etc
    player_id = Column(Integer, ForeignKey("players.id", ondelete="SET NULL"), nullable=True, index=True)
    is_starter = Column(Boolean, default=True, nullable=False)
    source = Column(String, nullable=True)  # e.g., "yahoo"
    __table_args__ = (
        UniqueConstraint("team_id", "week", "slot", name="uq_team_week_slot"),
    )

class Projection(Base):
    __tablename__ = "projections"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    week = Column(Integer, nullable=False, index=True)
    projected_points = Column(Float, nullable=False)
    variance = Column(Float, nullable=True)
    data = Column(JSON, nullable=False, default=dict)  # by-category breakdown
    computed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (
        UniqueConstraint("player_id", "week", name="uq_proj_player_week"),
        Index("ix_proj_week_player", "week", "player_id"),
    )

```
  
This schema matches usage in routers (players.py, waivers.py) and tests (test_db_schema.py, test_projection_api.py).  
  
⸻  
  
**4) Alembic configuration**  
  
**File:** apps/api/alembic.ini — leave as is, but we will set URL at runtime.  
  
**Replace** apps/api/alembic/env.py with:  
  
```
# apps/api/alembic/env.py
from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Prefer DATABASE_URL from environment (e.g., Neon). Fallback to ini.
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

from app.models import Base  # target metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

```
  
  
⸻  
  
**5) Initial migration**  
  
Run from repo root:  
  
```
cd apps/api
alembic revision --autogenerate -m "init schema"
alembic upgrade head

```
  
This must create tables: users, oauth_tokens, leagues, teams, players, player_links, roster_slots, projections, with constraints and indexes defined above.  
  
If autogenerate omits constraints, **edit the generated revision** under apps/api/alembic/versions/ to include:  
  
```
op.create_unique_constraint("uq_team_week_slot", "roster_slots", ["team_id","week","slot"])
op.create_unique_constraint("uq_proj_player_week", "projections", ["player_id","week"])
op.create_index("ix_proj_week_player", "projections", ["week","player_id"], unique=False)

```
op.create_unique_constraint("uq_league_yahoo_id", "leagues", ["yahoo_id"])  
  
  
⸻  
  
**6) Health check**  
  
**Edit:** apps/api/app/routers/health.py — implement DB check:  
  
```
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..deps import get_db

router = APIRouter()

@router.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

```
    return {"ok": True}  
  
  
⸻  
  
**7) Environment values**  
  
**File:** apps/api/.env.example — add/update:  
  
```
# Local (Docker/dev)
DATABASE_URL=postgresql+psycopg://ff:ff@db:5432/ff

# Neon (prod)

```
# DATABASE_URL=postgresql+psycopg:**//USER:PASSWORD@ep-xxxx.us-xx-x.aws.neon.tech/DB?sslmode=require**  
  
If you maintain a root .env.example, mirror the DATABASE_URL there as well.  
  
⸻  
  
**8) Render deploy hook**  
  
**File:** render.yaml — under the API service, ensure migrations run before start:  
  
```
services:
  - type: web
    name: api
    env: python
    rootDir: apps/api
    buildCommand: pip install -r requirements.txt
    preDeployCommand: alembic upgrade head

```
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT  
  
*(Keep other services and env vars unchanged.)*  
  
⸻  
  
**9) Minimal tests**  
  
**Create:** apps/api/tests/test_db.py  
  
```
from sqlalchemy import text
from app.deps import SessionLocal

def test_db_connects():
    with SessionLocal() as s:

```
        assert s.execute(text("SELECT 1")).scalar() == 1  
  
**Create:** apps/api/tests/test_models.py  
  
```
from app.deps import SessionLocal
from app.models import User

def test_user_crud():
    with SessionLocal() as s:
        u = User(email="test@example.com")
        s.add(u); s.commit(); s.refresh(u)

```
        assert u.id is not None  
  
The existing tests/conftest.py already configures an in‑memory SQLite engine and overrides get_db, so these tests will run with SQLite as well.  
  
⸻  
  
**10) Verification**  
  
Local (with Docker dev DB or Neon URL):  
  
```
cd apps/api
alembic upgrade head
python - <<'PY'
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.environ.get('DATABASE_URL', 'sqlite://'))
with engine.connect() as c:
    print(c.execute(text('select 1')).scalar())
PY

```
  
On Render: confirm deploy logs include alembic upgrade head and the app starts healthy.  
  
**Success criteria:** schema exists; /health returns 200; projections and waivers routes can read/write the expected tables without errors.  
