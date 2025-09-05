#!/usr/bin/env python3
# ruff: noqa
"""
Yahoo Data Synchronization Script

This script pulls data from Yahoo Fantasy API and updates the database.
Usage: python yahoo_sync.py <user_id>
"""
import os
import sys
import logging
from datetime import datetime, UTC
from typing import List, Dict, Any

import httpx
from sqlalchemy.orm import Session
from redis import Redis

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import (
    User,
    League,
    Team,
    Player,
    RosterSlot,
    Matchup,
    Projection,
    WaiverCandidate,
    StreamerSignal,
    YahooAccount,
)
from app.yahoo_oauth import YahooOAuthClient
from app.security import TokenEncryptionService
from app.settings import settings
from app.deps import get_db, get_token_encryption_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
db: Session | None = None
redis: Redis | None = None
yahoo_client: YahooOAuthClient | None = None
current_week: int = 1  # In a real implementation, this would be determined from the NFL schedule


def get_user_yahoo_tokens(user_id: int) -> Dict[str, Any]:
    """Get Yahoo OAuth tokens for a user"""
    global db
    if db is None:
        raise RuntimeError("DB session not initialized")

    # Get user's Yahoo account
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found")

    # Get Yahoo account
    yahoo_account = db.query(YahooAccount).filter(YahooAccount.user_id == user_id).first()
    if not yahoo_account:
        raise ValueError(f"No Yahoo account found for user {user_id}")

    return {
        "access_token": yahoo_account.access_token_enc,
        "refresh_token": yahoo_account.refresh_token_enc,
        "expires_at": yahoo_account.access_expires_at,
        "guid": yahoo_account.yahoo_guid,
    }


def sync_leagues(user_id: int) -> List[League]:
    """Sync user's Yahoo leagues"""
    global db, yahoo_client, current_week
    if db is None or yahoo_client is None:
        raise RuntimeError("Dependencies not initialized")
    assert db is not None and yahoo_client is not None

    # Get user's Yahoo tokens
    tokens = get_user_yahoo_tokens(user_id)

    # Make API request to get leagues
    # This is a simplified example - in a real implementation, you'd use the Yahoo Fantasy API
    leagues_data: list[dict[str, Any]] = []

    # Process each league
    for league_data in leagues_data:
        # Check if league exists
        league = db.query(League).filter(League.yahoo_league_id == league_data["id"]).first()

        if not league:
            # Create new league
            league = League(
                yahoo_league_id=league_data["id"],
                season=league_data["season"],
                name=league_data["name"],
                scoring_type=league_data["scoring_type"],
                roster_positions=league_data.get("roster_positions", []),
            )
            db.add(league)
            db.commit()
            db.refresh(league)
            logger.info(f"Created new league: {league.name} ({league.yahoo_league_id})")
        else:
            # Update existing league
            league.name = league_data["name"]
            league.scoring_type = league_data["scoring_type"]
            league.roster_positions = league_data.get("roster_positions", [])
            db.commit()
            logger.info(f"Updated league: {league.name} ({league.yahoo_league_id})")

        # Sync teams for this league
        sync_teams(league.id, user_id, league_data.get("teams", []))

    return (
        db.query(League).filter(League.yahoo_league_id.in_([l["id"] for l in leagues_data])).all()
    )


def sync_teams(league_id: int, user_id: int, teams_data: List[Dict[str, Any]]):
    """Sync teams for a league"""
    global db
    if db is None:
        raise RuntimeError("DB session not initialized")
    assert db is not None

    for team_data in teams_data:
        # Check if team exists
        team = (
            db.query(Team)
            .filter(Team.league_id == league_id, Team.yahoo_team_key == team_data["team_key"])
            .first()
        )

        if not team:
            # Create new team
            team = Team(
                league_id=league_id,
                yahoo_team_key=team_data["team_key"],
                name=team_data["name"],
                logo_url=team_data.get("logo_url"),
                manager_user_id=user_id if team_data.get("is_manager") else None,
            )
            db.add(team)
            db.commit()
            db.refresh(team)
            logger.info(f"Created new team: {team.name} in league {league_id}")
        else:
            # Update existing team
            team.name = team_data["name"]
            team.logo_url = team_data.get("logo_url")
            team.manager_user_id = user_id if team_data.get("is_manager") else team.manager_user_id
            db.commit()
            logger.info(f"Updated team: {team.name} in league {league_id}")

        # Sync roster for this team
        sync_roster(team.id, team_data.get("roster", []))


def sync_roster(team_id: int, roster_data: List[Dict[str, Any]]):
    """Sync roster for a team"""
    global db, current_week
    if db is None:
        raise RuntimeError("DB session not initialized")
    assert db is not None

    for slot_data in roster_data:
        # Check if player exists
        player = db.query(Player).filter(Player.yahoo_player_id == slot_data["player_id"]).first()

        if not player:
            # Create new player
            player = Player(
                yahoo_player_id=slot_data["player_id"],
                full_name=slot_data["name"],
                position_primary=slot_data["position"],
                nfl_team=slot_data.get("team"),
                bye_week=slot_data.get("bye_week"),
                status=slot_data.get("status"),
            )
            db.add(player)
            db.commit()
            db.refresh(player)
            logger.info(f"Created new player: {player.full_name} ({player.yahoo_player_id})")
        else:
            # Update existing player
            player.full_name = slot_data["name"]
            player.position_primary = slot_data["position"]
            player.nfl_team = slot_data.get("team")
            player.bye_week = slot_data.get("bye_week")
            player.status = slot_data.get("status")
            db.commit()
            logger.info(f"Updated player: {player.full_name} ({player.yahoo_player_id})")

        # Check if roster slot exists
        roster_slot = (
            db.query(RosterSlot)
            .filter(
                RosterSlot.team_id == team_id,
                RosterSlot.week == current_week,
                RosterSlot.slot == slot_data["slot"],
            )
            .first()
        )

        if not roster_slot:
            # Create new roster slot
            roster_slot = RosterSlot(
                team_id=team_id,
                week=current_week,
                slot=slot_data["slot"],
                player_id=player.id,
                projected_pts=slot_data.get("projected_points"),
                actual_pts=slot_data.get("actual_points"),
                is_starter=slot_data.get("is_starter", True),
            )
            db.add(roster_slot)
            db.commit()
            db.refresh(roster_slot)
            logger.info(
                f"Created new roster slot: {player.full_name} as {slot_data['slot']} for team {team_id}"
            )
        else:
            # Update existing roster slot
            roster_slot.player_id = player.id
            roster_slot.projected_pts = slot_data.get("projected_points")
            roster_slot.actual_pts = slot_data.get("actual_points")
            roster_slot.is_starter = slot_data.get("is_starter", True)
            db.commit()
            logger.info(
                f"Updated roster slot: {player.full_name} as {slot_data['slot']} for team {team_id}"
            )


def sync_matchups(league_id: int):
    """Sync matchups for a league"""
    global db, current_week
    if db is None:
        raise RuntimeError("DB session not initialized")
    assert db is not None

    # This is a simplified implementation
    # In a real implementation, you would fetch matchup data from Yahoo API

    # Get all teams in the league
    teams = db.query(Team).filter(Team.league_id == league_id).all()

    # Create matchups for each team
    for team in teams:
        # Check if matchup exists
        matchup = (
            db.query(Matchup)
            .filter(
                Matchup.league_id == league_id,
                Matchup.week == current_week,
                Matchup.team_id == team.id,
            )
            .first()
        )

        if not matchup:
            # Create new matchup with opponent as NULL (to be filled later)
            matchup = Matchup(
                league_id=league_id,
                week=current_week,
                team_id=team.id,
                opponent_team_id=None,
                projected_pts=0.0,
                actual_pts=0.0,
            )
            db.add(matchup)
            db.commit()
            db.refresh(matchup)
            logger.info(f"Created new matchup: {team.name} in league {league_id}")
        else:
            logger.info(f"Matchup already exists: {team.name} in league {league_id}")


def main(user_id: int):
    """Main sync function"""
    global db, redis, yahoo_client, current_week

    try:
        # Initialize dependencies
        db = next(get_db())
        redis = Redis.from_url(settings.redis_url)
        encryption = get_token_encryption_service()
        yahoo_client = YahooOAuthClient(encryption)

        logger.info(f"Starting sync for user {user_id}")

        # Sync leagues
        leagues = sync_leagues(user_id)
        logger.info(f"Synced {len(leagues)} leagues")

        # Sync matchups for each league
        for league in leagues:
            sync_matchups(league.id)

        logger.info("Sync completed successfully")

    except Exception as e:
        logger.error(f"Sync failed: {str(e)}")
        raise
    finally:
        # Clean up
        if db:
            db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python yahoo_sync.py <user_id>")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("Error: user_id must be an integer")
        sys.exit(1)

    main(user_id)
