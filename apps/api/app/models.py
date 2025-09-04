# apps/api/app/models.py
from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import (
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
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


# ----------------------
# Auth & Identity
# ----------------------
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    yahoo_guid: Mapped[str | None] = mapped_column(Text, unique=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    oauth_tokens: Mapped[list[OAuthToken]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    teams: Mapped[list[Team]] = relationship(back_populates="manager")
    preferences: Mapped[UserPreferences | None] = relationship(back_populates="user", uselist=False)
    notes: Mapped[list[Note]] = relationship(back_populates="user")


class WebSession(Base):
    __tablename__ = "sessions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_agent: Mapped[str | None] = mapped_column(Text)
    ip_addr: Mapped[str | None] = mapped_column(String)
    user: Mapped[User] = relationship()


class YahooAccount(Base):
    __tablename__ = "yahoo_accounts"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    yahoo_guid: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    scope: Mapped[str | None] = mapped_column(Text)
    access_token_enc: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_enc: Mapped[str] = mapped_column(Text, nullable=False)
    access_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user: Mapped[User] = relationship()


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String, nullable=False)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scope: Mapped[str | None] = mapped_column(Text)
    guid: Mapped[str | None] = mapped_column(String, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user: Mapped[User] = relationship(back_populates="oauth_tokens")


# ----------------------
# League & Team
# ----------------------
class League(Base):
    __tablename__ = "leagues"
    id: Mapped[int] = mapped_column(primary_key=True)
    yahoo_league_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    season: Mapped[int | None] = mapped_column(SmallInteger)
    name: Mapped[str] = mapped_column(String, nullable=False)
    scoring_type: Mapped[str | None] = mapped_column(String)
    roster_positions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    teams: Mapped[list[Team]] = relationship(back_populates="league")

    # Backwards-compatible alias expected by tests. Use hybrid_property so
    # SQLAlchemy can use it inside query expressions (tests do select(League).where(League.yahoo_id == ...)).
    @hybrid_property
    def yahoo_id(self) -> str:
        """Return the Yahoo league identifier used by tests."""
        return self.yahoo_league_id

    @yahoo_id.setter  # type: ignore[no-redef]
    def yahoo_id(self, v: str | int) -> None:
        """Persist the identifier as a string to match the column type."""
        self.yahoo_league_id = str(v)


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    yahoo_team_key: Mapped[str | None] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, nullable=False)
    logo_url: Mapped[str | None] = mapped_column(Text)
    manager_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    league: Mapped[League] = relationship(back_populates="teams")
    manager: Mapped[User | None] = relationship()
    roster_slots: Mapped[list[RosterSlot]] = relationship(back_populates="team")
    matchups: Mapped[list[Matchup]] = relationship(
        back_populates="team", foreign_keys="Matchup.team_id"
    )
    waiver_candidates: Mapped[list[WaiverCandidate]] = relationship(back_populates="team")
    __table_args__ = (UniqueConstraint("league_id", "yahoo_team_key"),)


# ----------------------
# Players
# ----------------------
class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True)
    yahoo_player_id: Mapped[str | None] = mapped_column(String, unique=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    position_primary: Mapped[str | None] = mapped_column(String)
    nfl_team: Mapped[str | None] = mapped_column(String)
    bye_week: Mapped[int | None] = mapped_column(SmallInteger)
    status: Mapped[str | None] = mapped_column(String)
    meta: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    roster_slots: Mapped[list[RosterSlot]] = relationship(back_populates="player")
    projections: Mapped[list[Projection]] = relationship(back_populates="player")
    notes: Mapped[list[Note]] = relationship(back_populates="player")
    waiver_candidates: Mapped[list[WaiverCandidate]] = relationship(back_populates="player")
    streamer_signals: Mapped[list[StreamerSignal]] = relationship(back_populates="player")
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
    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    week: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    slot: Mapped[str | None] = mapped_column(String)
    player_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("players.id", ondelete="SET NULL"), index=True
    )
    projected_pts: Mapped[float | None] = mapped_column(Float)
    actual_pts: Mapped[float | None] = mapped_column(Float)
    is_starter: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    team: Mapped[Team] = relationship(back_populates="roster_slots")
    player: Mapped[Player | None] = relationship(back_populates="roster_slots")
    __table_args__ = (
        UniqueConstraint("team_id", "week", "slot", name="uq_team_week_slot"),
        Index("idx_roster_slots_team_week", "team_id", "week"),
    )


class Matchup(Base):
    __tablename__ = "matchups"
    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opponent_team_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="SET NULL"), index=True
    )
    projected_pts: Mapped[float | None] = mapped_column(Float)
    actual_pts: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    league: Mapped[League] = relationship()
    team: Mapped[Team] = relationship(foreign_keys=[team_id], back_populates="matchups")
    opponent_team: Mapped[Team | None] = relationship(foreign_keys=[opponent_team_id])
    __table_args__ = (
        UniqueConstraint("league_id", "week", "team_id", name="uq_matchups_league_week_team"),
        Index("idx_matchups_league_week", "league_id", "week"),
    )


class Projection(Base):
    __tablename__ = "projections"
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    source: Mapped[str] = mapped_column(
        String, nullable=False, default="internal", server_default="internal"
    )
    projected_points: Mapped[float] = mapped_column(Float, nullable=False)
    variance: Mapped[float | None] = mapped_column(Float)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    player: Mapped[Player] = relationship(back_populates="projections")
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
    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    team_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    delta_xfp: Mapped[float | None] = mapped_column(Float)
    fit_score: Mapped[float | None] = mapped_column(Float)
    faab_suggestion: Mapped[int | None] = mapped_column(Integer)
    acquisition_prob: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    league: Mapped[League] = relationship()
    player: Mapped[Player] = relationship(back_populates="waiver_candidates")
    team: Mapped[Team] = relationship(back_populates="waiver_candidates")
    __table_args__ = (UniqueConstraint("league_id", "week", "player_id"),)


class StreamerSignal(Base):
    __tablename__ = "streamer_signals"
    id: Mapped[int] = mapped_column(primary_key=True)
    week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    subject_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fit_score: Mapped[float | None] = mapped_column(Float)
    weather_bucket: Mapped[int | None] = mapped_column(SmallInteger)
    meta: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    player_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        index=True,
    )
    player: Mapped[Player | None] = relationship(
        back_populates="streamer_signals", foreign_keys=[player_id]
    )
    __table_args__ = (UniqueConstraint("week", "kind", "subject_id"),)


# ----------------------
# User Preferences, Notes, Events
# ----------------------
class UserPreferences(Base):
    __tablename__ = "user_preferences"
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    theme: Mapped[str] = mapped_column(String, nullable=False, default="system")
    saved_views: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    pinned_players: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user: Mapped[User] = relationship(back_populates="preferences")


class Note(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    note: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user: Mapped[User] = relationship(back_populates="notes")
    player: Mapped[Player] = relationship(back_populates="notes")
    __table_args__ = (Index("idx_notes_user_player", "user_id", "player_id"),)


class EventLog(Base):
    __tablename__ = "event_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    __table_args__ = (Index("idx_event_log_ts", "ts"),)


# ----------------------
# Jobs & Job Runs
# ----------------------
class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    not_before: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String, nullable=False, default="queued")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    runs: Mapped[list[JobRun]] = relationship(back_populates="job", cascade="all, delete-orphan")


class JobRun(Base):
    __tablename__ = "job_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ok: Mapped[bool | None] = mapped_column(Boolean)
    message: Mapped[str | None] = mapped_column(String)
    job: Mapped[Job] = relationship(back_populates="runs")
