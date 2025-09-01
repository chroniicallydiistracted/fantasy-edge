from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    func,
    Boolean,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    oauth_tokens = relationship("OAuthToken", back_populates="user")


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # e.g., "yahoo"
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    expires_at = Column(DateTime(timezone=True))
    scope = Column(Text)
    guid = Column(String, unique=True, index=True)  # Yahoo-specific GUID

    # Relationships
    user = relationship("User", back_populates="oauth_tokens")


class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    yahoo_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)

    teams = relationship("Team", back_populates="league")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    name = Column(String, nullable=False)
    yahoo_id = Column(Integer, nullable=True)

    league = relationship("League", back_populates="teams")
    roster_slots = relationship("RosterSlot", back_populates="team")


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    position = Column(String, nullable=True)

    roster_slots = relationship("RosterSlot", back_populates="player")
    injuries = relationship("Injury", back_populates="player")
    baselines = relationship("Baseline", back_populates="player")
    projections = relationship("Projection", back_populates="player")
    recommendations = relationship("Recommendation", back_populates="player")
    link = relationship("PlayerLink", back_populates="player", uselist=False)


class RosterSlot(Base):
    __tablename__ = "roster_slots"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    week = Column(Integer, nullable=False)
    position = Column(String, nullable=True)

    team = relationship("Team", back_populates="roster_slots")
    player = relationship("Player", back_populates="roster_slots")


class Injury(Base):
    __tablename__ = "injuries"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    status = Column(String, nullable=False)
    report_time = Column(DateTime(timezone=True), nullable=False)

    player = relationship("Player", back_populates="injuries")


class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, unique=True, nullable=False, index=True)
    waf = Column(Float, nullable=False)


class Baseline(Base):
    __tablename__ = "baselines"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    metric = Column(String, nullable=False)
    value = Column(Float, nullable=False)

    player = relationship("Player", back_populates="baselines")


class Projection(Base):
    __tablename__ = "projections"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    week = Column(Integer, nullable=False)
    projected_points = Column(Float, nullable=False)

    player = relationship("Player", back_populates="projections")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    recommendation = Column(String, nullable=False)
    reason = Column(Text, nullable=True)

    player = relationship("Player", back_populates="recommendations")


class PlayerLink(Base):
    __tablename__ = "player_links"

    player_id = Column(Integer, ForeignKey("players.id"), primary_key=True)
    yahoo_key = Column(String, unique=True, nullable=True, index=True)
    gsis_id = Column(String, unique=True, nullable=True, index=True)
    pfr_id = Column(String, unique=True, nullable=True, index=True)
    last_manual_override = Column(Boolean, default=False, nullable=False)

    player = relationship("Player", back_populates="link")
