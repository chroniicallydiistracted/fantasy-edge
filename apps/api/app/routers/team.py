from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..deps import get_db, get_current_user_session
from ..models import Team, RosterSlot, Matchup, Player, Projection

router = APIRouter()

@router.get("/{team_id}/roster")
def get_team_roster(
    team_id: int,
    week: Optional[int] = Query(None, description="Week number"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_session)
):
    """Get roster slots for a specific team and week"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    query = db.query(RosterSlot).filter(RosterSlot.team_id == team_id)
    if week is not None:
        query = query.filter(RosterSlot.week == week)

    roster_slots = query.all()
    return roster_slots

@router.get("/{team_id}/matchup")
def get_team_matchup(
    team_id: int,
    week: Optional[int] = Query(None, description="Week number"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_session)
):
    """Get matchup for a specific team and week"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    query = db.query(Matchup).filter(Matchup.team_id == team_id)
    if week is not None:
        query = query.filter(Matchup.week == week)

    matchup = query.first()
    return matchup

@router.get("/{team_id}/waivers")
def get_team_waivers(
    team_id: int,
    week: Optional[int] = Query(None, description="Week number"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_session)
):
    """Get waiver candidates for a specific team and week"""
    from ..models import WaiverCandidate

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    query = db.query(WaiverCandidate).filter(WaiverCandidate.league_id == team.league_id)
    if week is not None:
        query = query.filter(WaiverCandidate.week == week)

    waiver_candidates = query.all()
    return waiver_candidates
