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
