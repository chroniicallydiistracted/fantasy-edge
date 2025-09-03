from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..deps import get_db, get_current_user_session
from ..models import Player, Projection

router = APIRouter()


@router.get("/{player_id}/projection")
def get_player_projection(
    player_id: int,
    week: Optional[int] = Query(None, description="Week number"),
    source: Optional[str] = Query(None, description="Projection source"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_session),
):
    """Get projection for a specific player, week, and source"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    query = db.query(Projection).filter(Projection.player_id == player_id)
    if week is not None:
        query = query.filter(Projection.week == week)
    if source is not None:
        query = query.filter(Projection.source == source)

    projection = query.first()
    if not projection:
        raise HTTPException(status_code=404, detail="Projection not found")
    # Return a serializable dict matching test expectations
    return {
        "player_id": projection.player_id,
        "week": projection.week,
        "projected_points": projection.projected_points,
        "variance": projection.variance,
        "data": projection.data,
        "source": projection.source,
    }
