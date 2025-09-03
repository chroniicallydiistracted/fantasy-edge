from fastapi import APIRouter

router = APIRouter()


@router.get("/{team_id}/optimize")
def optimize(team_id: int, week: int):
    # Stub: will call OR-Tools later
    return {"team_id": team_id, "week": week, "lineup": [], "alts": []}
