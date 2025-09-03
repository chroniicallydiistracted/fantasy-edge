from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user_session
from ..models import League, Team

router = APIRouter()


@router.get("/")
def get_leagues(db: Session = Depends(get_db), current_user=Depends(get_current_user_session)):
    """Get all leagues for the current user"""
    # In a real implementation, we would filter by user's leagues
    leagues = db.query(League).all()
    return leagues


@router.get("/{league_id}/teams")
def get_league_teams(
    league_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user_session)
):
    """Get all teams in a specific league"""
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    teams = db.query(Team).filter(Team.league_id == league_id).all()
    return teams
