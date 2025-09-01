from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user_session, get_yahoo_client
from ..models import User
from ..yahoo_client import YahooFantasyClient

router = APIRouter()


def _scoring_map(data):
    scoring = {}
    try:
        league = data.get("fantasy_content", {}).get("league")
        if isinstance(league, list):
            league = league[1]
        stats = league.get("settings", {}).get("stat_categories", {}).get("stats", [])
        for stat in stats:
            st = stat.get("stat", {})
            sid = st.get("stat_id")
            name = st.get("display_name") or st.get("name")
            if sid is not None and name:
                scoring[str(sid)] = name
    except Exception:
        pass
    return scoring


@router.get("/leagues")
def list_leagues(
    current_user: User = Depends(get_current_user_session),
    db: Session = Depends(get_db),
    client: YahooFantasyClient = Depends(get_yahoo_client),
):
    return client.get(db, current_user, "/users;use_login=1/games;game_keys=nfl/leagues")


@router.get("/league/{league_key}")
def league_meta(
    league_key: str,
    current_user: User = Depends(get_current_user_session),
    db: Session = Depends(get_db),
    client: YahooFantasyClient = Depends(get_yahoo_client),
):
    data = client.get(db, current_user, f"/league/{league_key}")
    return {"raw": data, "scoring": _scoring_map(data)}


@router.get("/league/{league_key}/teams")
def league_teams(
    league_key: str,
    current_user: User = Depends(get_current_user_session),
    db: Session = Depends(get_db),
    client: YahooFantasyClient = Depends(get_yahoo_client),
):
    return client.get(db, current_user, f"/league/{league_key}/teams")


@router.get("/league/{league_key}/rosters")
def league_rosters(
    league_key: str,
    week: int,
    current_user: User = Depends(get_current_user_session),
    db: Session = Depends(get_db),
    client: YahooFantasyClient = Depends(get_yahoo_client),
):
    return client.get(db, current_user, f"/league/{league_key}/rosters", params={"week": str(week)})


@router.get("/league/{league_key}/matchups")
def league_matchups(
    league_key: str,
    week: int,
    current_user: User = Depends(get_current_user_session),
    db: Session = Depends(get_db),
    client: YahooFantasyClient = Depends(get_yahoo_client),
):
    return client.get(
        db, current_user, f"/league/{league_key}/matchups", params={"week": str(week)}
    )
