from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user_session
from ..models import Player, Projection, User

router = APIRouter()


def _streamers_by_position(db: Session, week: int, position: str):
    rows = (
        db.query(Player, Projection.projected_points)
        .join(Projection, (Player.id == Projection.player_id) & (Projection.week == week))
        .filter(Player.position == position)
        .order_by(Projection.projected_points.desc(), Player.id.asc())
        .all()
    )
    return [
        {
            "player_id": p.id,
            "name": p.name,
            "projected_points": round(points, 2),
            "rank": idx + 1,
        }
        for idx, (p, points) in enumerate(rows)
    ]


@router.get("/def")
def def_streamers(
    week: int,
    current_user: User = Depends(get_current_user_session),
    db: Session = Depends(get_db),
):
    return _streamers_by_position(db, week, "DEF")


@router.get("/idp")
def idp_streamers(
    week: int,
    current_user: User = Depends(get_current_user_session),
    db: Session = Depends(get_db),
):
    return _streamers_by_position(db, week, "IDP")
