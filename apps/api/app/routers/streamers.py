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
    """Get streamer signals for a specific kind and week.

    Returns player_id, name, projected_points, and a 1-based rank.
    """
    if kind not in ["def", "idp"]:
        raise HTTPException(status_code=400, detail="Invalid kind. Must be 'def' or 'idp'")

    q = (
        db.query(Projection, Player)
        .join(Player, Player.id == Projection.player_id)
        .filter(Projection.week == week)
        .filter(Player.position_primary.in_(["DEF", "IDP"]))
        .filter(Projection.player_id.isnot(None))
    )
    pos = {"def": "DEF", "idp": "IDP"}[kind]
    q = q.filter(Player.position_primary == pos)
    rows = q.order_by(Projection.projected_points.desc(), Player.id.asc()).all()
    results = []
    for idx, (proj, player) in enumerate(rows, start=1):
        results.append(
            {
                "player_id": player.id,
                "name": player.full_name,
                "projected_points": proj.projected_points,
                "rank": idx,
            }
        )
    return results
