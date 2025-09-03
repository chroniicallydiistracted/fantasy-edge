# apps/api/app/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    Float,
    JSON,
    UUID,
    SmallInteger,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.hybrid import hybrid_property
import uuid

Base = declarative_base()


# ----------------------
# Auth & Identity
# ----------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    yahoo_guid = Column(Text, unique=True)  # Yahoo user unique guid
    email = Column(String, unique=True, index=True, nullable=True)
    display_name = Column(Text, nullable=True)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    oauth_tokens = relationship("OAuthToken", back_populates="user", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="manager")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    notes = relationship("Note", back_populates="user")


class WebSession(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    user_agent = Column(Text, nullable=True)
    ip_addr = Column(String, nullable=True)
    # relationships
    user = relationship("User")


class YahooAccount(Base):
    __tablename__ = "yahoo_accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    yahoo_guid = Column(Text, nullable=False, unique=True)  # belt & suspenders
    scope = Column(Text, nullable=True)
    access_token_enc = Column(Text, nullable=False)  # Fernet encrypted
    refresh_token_enc = Column(Text, nullable=False)  # Fernet encrypted
    access_expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    user = relationship("User")


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
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
    yahoo_league_id = Column(String, nullable=False, unique=True)  # e.g., "406.l.12345"
    # Allow tests to create League without providing season/scoring_type
    season = Column(SmallInteger, nullable=True)
    name = Column(String, nullable=False)
    scoring_type = Column(String, nullable=True)  # "point", "headpoint" etc
    roster_positions = Column(JSON, nullable=False, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    teams = relationship("Team", back_populates="league")

    # Backwards-compatible alias expected by tests. Use hybrid_property so
    # SQLAlchemy can use it inside query expressions (tests do select(League).where(League.yahoo_id == ...)).
    @hybrid_property
    def yahoo_id(self):
        return self.yahoo_league_id

    @yahoo_id.setter
    def yahoo_id(self, v):
        # store as string to match the underlying column type
        self.yahoo_league_id = str(v) if v is not None else None


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    league_id = Column(
        Integer,
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    yahoo_team_key = Column(String, nullable=True)
    name = Column(String, nullable=False)
    logo_url = Column(Text, nullable=True)
    manager_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    league = relationship("League", back_populates="teams")
    manager = relationship("User")
    roster_slots = relationship("RosterSlot", back_populates="team")
    # There are two foreign keys on Matchup pointing to Team (team_id and opponent_team_id).
    # Specify foreign_keys so SQLAlchemy can determine the correct join for Team.matchups.
    matchups = relationship("Matchup", back_populates="team", foreign_keys="Matchup.team_id")
    waiver_candidates = relationship("WaiverCandidate", back_populates="team")
    __table_args__ = (UniqueConstraint("league_id", "yahoo_team_key"),)


# ----------------------
# Players
# ----------------------
class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    yahoo_player_id = Column(String, unique=True, nullable=True)  # nullable for custom rows
    full_name = Column(String, nullable=False)
    position_primary = Column(String, nullable=True)  # e.g., "WR", "RB"
    nfl_team = Column(String, nullable=True)  # e.g., "KC"
    bye_week = Column(SmallInteger, nullable=True)
    status = Column(String, nullable=True)  # OUT, Q, IR, etc.
    meta = Column(JSON, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    roster_slots = relationship("RosterSlot", back_populates="player")
    projections = relationship("Projection", back_populates="player")
    notes = relationship("Note", back_populates="player")
    waiver_candidates = relationship("WaiverCandidate", back_populates="player")
    streamer_signals = relationship("StreamerSignal", back_populates="player")
    __table_args__ = (Index("idx_players_pos", "position_primary"),)

    # Backwards-compatible aliases for tests
    @property
    def name(self):
        return self.full_name

    @name.setter
    def name(self, v):
        self.full_name = v

    @property
    def position(self):
        return self.position_primary

    @position.setter
    def position(self, v):
        self.position_primary = v


# ----------------------
# Roster, Matchups, Projections
# ----------------------
class RosterSlot(Base):
    __tablename__ = "roster_slots"
    id = Column(Integer, primary_key=True)
    team_id = Column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    week = Column(SmallInteger, nullable=False, index=True)
    slot = Column(String, nullable=True)  # e.g., QB,RB,WR,TE,FLEX,BENCH,DEF,K,IDP
    player_id = Column(
        Integer,
        ForeignKey("players.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    projected_pts = Column(Float, nullable=True)
    actual_pts = Column(Float, nullable=True)
    is_starter = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    team = relationship("Team", back_populates="roster_slots")
    player = relationship("Player", back_populates="roster_slots")
    __table_args__ = (
        UniqueConstraint("team_id", "week", "slot", name="uq_team_week_slot"),
        Index("idx_roster_slots_team_week", "team_id", "week"),
    )


class Matchup(Base):
    __tablename__ = "matchups"
    id = Column(Integer, primary_key=True)
    league_id = Column(
        Integer,
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week = Column(SmallInteger, nullable=False, index=True)
    team_id = Column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opponent_team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    projected_pts = Column(Float, nullable=True)
    actual_pts = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    league = relationship("League")
    team = relationship("Team", foreign_keys=[team_id], back_populates="matchups")
    opponent_team = relationship("Team", foreign_keys=[opponent_team_id])
    __table_args__ = (
        UniqueConstraint("league_id", "week", "team_id", name="uq_matchups_league_week_team"),
        Index("idx_matchups_league_week", "league_id", "week"),
    )


class Projection(Base):
    __tablename__ = "projections"
    id = Column(Integer, primary_key=True)
    player_id = Column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week = Column(SmallInteger, nullable=False, index=True)
    source = Column(
        String, nullable=False, default="internal", server_default="internal"
    )  # "yahoo", "internal", etc.
    projected_points = Column(Float, nullable=False)
    variance = Column(Float, nullable=True)
    data = Column(JSON, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    player = relationship("Player", back_populates="projections")
    __table_args__ = (
        UniqueConstraint("player_id", "week", "source", name="uq_projections_player_week_source"),
        Index("idx_projections_week", "week"),
    )

    def __init__(self, **kwargs):
        # Ensure a source value exists for NOT NULL constraint in tests
        if "source" not in kwargs or kwargs.get("source") is None:
            kwargs["source"] = "internal"
        # allow callers to pass 'data' as a dict; SQLAlchemy will handle JSON serialization
        super().__init__(**kwargs)


# ----------------------
# Waivers, Streamers
# ----------------------
class WaiverCandidate(Base):
    __tablename__ = "waiver_candidates"
    id = Column(Integer, primary_key=True)
    league_id = Column(
        Integer,
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week = Column(SmallInteger, nullable=False, index=True)
    player_id = Column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    team_id = Column(
        Integer,
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    delta_xfp = Column(Float, nullable=True)  # Δ expected fantasy points vs worst starter
    fit_score = Column(Float, nullable=True)
    faab_suggestion = Column(Integer, nullable=True)
    acquisition_prob = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    league = relationship("League")
    player = relationship("Player", back_populates="waiver_candidates")
    team = relationship("Team", back_populates="waiver_candidates")
    __table_args__ = (UniqueConstraint("league_id", "week", "player_id"),)


class StreamerSignal(Base):
    __tablename__ = "streamer_signals"
    id = Column(Integer, primary_key=True)
    week = Column(SmallInteger, nullable=False)
    kind = Column(String, nullable=False)  # "def" | "idp"
    subject_id = Column(Integer, nullable=False)  # team_id for DEF; player_id for IDP
    fit_score = Column(Float, nullable=True)
    weather_bucket = Column(SmallInteger, nullable=True)  # 0..4 categorical
    meta = Column(JSON, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # optional foreign key to player for IDP signals
    player_id = Column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    # relationships
    player = relationship("Player", back_populates="streamer_signals", foreign_keys=[player_id])
    __table_args__ = (UniqueConstraint("week", "kind", "subject_id"),)


# ----------------------
# User Preferences, Notes, Events
# ----------------------
class UserPreferences(Base):
    __tablename__ = "user_preferences"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    theme = Column(String, nullable=False, default="system")
    saved_views = Column(JSON, nullable=False, default="{}")
    pinned_players = Column(JSON, nullable=False, default="[]")
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    user = relationship("User", back_populates="preferences")


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    note = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    user = relationship("User", back_populates="notes")
    player = relationship("Player", back_populates="notes")
    __table_args__ = (Index("idx_notes_user_player", "user_id", "player_id"),)


class EventLog(Base):
    __tablename__ = "event_log"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    type = Column(String, nullable=False)  # 'injury'|'weather'|'role'|'lock'|'refresh'
    payload = Column(JSON, nullable=False)
    __table_args__ = (Index("idx_event_log_ts", "ts"),)


# ----------------------
# Jobs & Job Runs
# ----------------------
class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kind = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    not_before = Column(DateTime(timezone=True), nullable=True)
    attempts = Column(SmallInteger, nullable=False, default=0)
    status = Column(String, nullable=False, default="queued")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationships
    runs = relationship("JobRun", back_populates="job", cascade="all, delete-orphan")


class JobRun(Base):
    __tablename__ = "job_runs"
    id = Column(Integer, primary_key=True)
    job_id = Column(UUID, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    ok = Column(Boolean, nullable=True)
    message = Column(String, nullable=True)
    # relationships
    job = relationship("Job", back_populates="runs")
