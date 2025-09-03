from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..deps import get_db, get_current_user_session
from ..models import Projection, Player

router = APIRouter()


@router.get("/{kind}")
def get_streamers(
    kind: str,  # "def" or "idp"
    week: Optional[int] = Query(None, description="Week number"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_session),
):
    """Get streamer signals for a specific kind and week"""
    if kind not in ["def", "idp"]:
        raise HTTPException(
            status_code=400, detail="Invalid kind. Must be 'def' or 'idp'"
        )

    # Build streamer list from projections and player positions to match tests
    q = (
        db.query(Projection, Player)
        .join(Player, Player.id == Projection.player_id)
        .filter(Projection.week == week)
        .filter(Player.position_primary.in_(["DEF", "IDP"]))
        .filter(Projection.player_id.isnot(None))
    )
    # filter kind: def -> position 'DEF', idp -> 'IDP'
    kind_map = {"def": "DEF", "idp": "IDP"}
    pos = kind_map.get(kind)
    q = q.filter(Player.position_primary == pos)
    rows = q.order_by(Projection.projected_points.desc()).all()
    results = []
    for proj, player in rows:
        results.append(
            {"player_id": player.id, "projected_points": proj.projected_points}
        )
    return results
