from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user_session
from ..models import User
from ..waivers import compute_waiver_shortlist

router = APIRouter()


@router.get("/{team_id}/waivers")
def team_waivers(
    team_id: int,
    week: int,
    horizon: int = 1,
    current_user: User = Depends(get_current_user_session),
    db: Session = Depends(get_db),
):
    """Return waiver shortlist for a team and week."""
    waivers = compute_waiver_shortlist(db, team_id, week, horizon)
    return {"team_id": team_id, "week": week, "waivers": waivers}
