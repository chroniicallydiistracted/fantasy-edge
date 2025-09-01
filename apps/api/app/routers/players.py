from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user_session
from ..models import Projection, User

router = APIRouter()


@router.get("/{player_id}/projection")
def get_projection(
    player_id: int,
    week: int,
    current_user: User = Depends(get_current_user_session),
    db: Session = Depends(get_db),
):
    """Return a projection for a player and week."""
    proj = db.query(Projection).filter_by(player_id=player_id, week=week).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Projection not found")
    return {
        "player_id": player_id,
        "week": week,
        "projected_points": proj.projected_points,
        "variance": proj.variance,
        "data": proj.data,
    }
