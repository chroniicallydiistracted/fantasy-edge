from typing import Any, Dict, List

from sqlalchemy.orm import Session

from .models import Player, Projection, RosterSlot


def compute_waiver_shortlist(
    session: Session, team_id: int, week: int, horizon: int = 1
) -> List[Dict[str, Any]]:
    """Rank free agents by projected improvement over the worst starter."""

    roster_ids = [
        rs.player_id
        for rs in session.query(RosterSlot.player_id).filter_by(
            team_id=team_id, week=week
        )
    ]
    if not roster_ids:
        return []

    worst_proj = (
        session.query(Projection.projected_points)
        .filter(Projection.player_id.in_(roster_ids), Projection.week == week)
        .order_by(Projection.projected_points.asc())
        .limit(1)
        .scalar()
    )
    if worst_proj is None:
        return []

    candidates = (
        session.query(Player, Projection.projected_points)
        .join(
            Projection, (Player.id == Projection.player_id) & (Projection.week == week)
        )
        .filter(~Player.id.in_(roster_ids))
        .all()
    )

    results: List[Dict[str, Any]] = []
    acquisition_prob = max(0.0, 1.0 - 0.1 * (horizon - 1))
    for player, proj in candidates:
        results.append(
            {
                "player_id": player.id,
                "name": player.name,
                "projected_points": proj,
                "delta_xfp": proj - worst_proj,
                "acquisition_prob": acquisition_prob,
            }
        )

    # Sort by delta descending, tie-break by player_id ascending to match test expectations
    results.sort(key=lambda x: (-x["delta_xfp"], x["player_id"]))
    # Assign an order 1..N for the shortlist
    for idx, r in enumerate(results, start=1):
        r["order"] = idx
    return results
