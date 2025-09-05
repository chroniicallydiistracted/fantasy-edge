import csv
import os
import sys
from datetime import datetime
from pathlib import Path
import importlib
from types import ModuleType
from typing import Any, Dict

import requests
import uvicorn
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from celery_app import celery  # type: ignore

# Make app models importable when running from this directory
sys.path.append(str(Path(__file__).resolve().parents[2] / "apps/api"))
sys.path.append(str(Path(__file__).resolve().parents[2] / "packages/projections"))
sys.path.append(str(Path(__file__).resolve().parents[2] / "packages"))
sys.path.append(str(Path(__file__).resolve().parents[2] / "packages/scoring"))


models: ModuleType | None
try:  # pragma: no cover - optional models
    models = importlib.import_module("app.models")
except Exception:  # pragma: no cover - optional models
    models = None

League: Any = getattr(models, "League", None) if models else None
Player: Any = getattr(models, "Player", None) if models else None
Projection: Any = getattr(models, "Projection", None) if models else None
Weather: Any = getattr(models, "Weather", None) if models else None
Injury: Any = getattr(models, "Injury", None) if models else None
PlayerLink: Any = getattr(models, "PlayerLink", None) if models else None
from app.waiver_service import compute_waiver_shortlist  # type: ignore  # noqa: E402
from projections import project_offense  # type: ignore  # noqa: E402


DATABASE_URL = os.getenv("DATABASE_URL")
try:
    engine = create_engine(DATABASE_URL) if DATABASE_URL else None
except Exception:  # pragma: no cover - missing driver
    engine = None
SessionLocal: sessionmaker[Session] | None = (
    sessionmaker(bind=engine) if engine else None
)

DATA_PATH = Path(os.getenv("DATA_PATH", "/data"))


@celery.task
def ping() -> str:
    return "pong"


def fetch_and_cache(url: str, dest: Path) -> Path:
    """Fetch a file supporting ETag caching."""

    etag_file = dest.with_suffix(dest.suffix + ".etag")
    headers: Dict[str, str] = {}
    if etag_file.exists():
        headers["If-None-Match"] = etag_file.read_text()

    resp = requests.get(url, headers=headers)
    if resp.status_code == 304 and dest.exists():
        return dest
    resp.raise_for_status()

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(resp.content)
    etag = resp.headers.get("ETag")
    if etag:
        etag_file.write_text(etag)
    return dest


@celery.task
def fetch_nflverse(url: str) -> str:
    """Download nflverse resource to the shared data path."""

    dest = DATA_PATH / Path(url).name
    return str(fetch_and_cache(url, dest))


def ingest_injuries_from_csv(path: Path, session: Session) -> int:
    """Normalize injuries CSV into the database."""

    if Injury is None or PlayerLink is None:
        return 0

    count = 0
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            gsis_id = row.get("gsis_id")
            status = row.get("status")
            report = row.get("report_date") or row.get("report_time")
            if not (gsis_id and status and report):
                continue
            link = session.query(PlayerLink).filter_by(gsis_id=gsis_id).first()
            if not link:
                continue
            injury = Injury(
                player_id=link.player_id,
                status=status,
                report_time=datetime.fromisoformat(report.replace("Z", "+00:00")),
            )
            session.add(injury)
            count += 1
    session.commit()
    return count


@celery.task
def ingest_injuries(csv_path: str) -> int:
    if SessionLocal is None:
        return 0
    session: Session = SessionLocal()
    try:
        return ingest_injuries_from_csv(Path(csv_path), session)
    finally:
        session.close()


def compute_waf(forecast: Dict[str, Any]) -> float:
    """Compute a simple Weather Adjustment Factor from NWS forecast."""

    period = forecast["properties"]["periods"][0]
    wind_str = period.get("windSpeed", "0 mph").split()[0]
    try:
        wind = int(wind_str)
    except ValueError:
        wind = 0
    precip = period.get("probabilityOfPrecipitation", {}).get("value") or 0
    waf = 1.0
    if wind > 15:
        waf -= 0.1
    if precip > 50:
        waf -= 0.1
    return round(max(waf, 0.5), 2)


@celery.task
def update_weather(game_id: str, lat: float, lon: float) -> float:
    """Fetch NWS forecast and store WAF for a game."""

    headers = {
        "User-Agent": os.getenv(
            "NWS_USER_AGENT", "Fantasy Edge (contact: you@example.com)"
        )
    }
    url = f"https://api.weather.gov/points/{lat},{lon}/forecast"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    waf = compute_waf(resp.json())
    if SessionLocal is None or Weather is None:
        return waf
    session: Session = SessionLocal()
    try:
        session.merge(Weather(game_id=game_id, waf=waf))
        session.commit()
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
    return waf


def generate_projections(session: Session, week: int) -> int:
    players = session.query(Player).all()
    count = 0
    for player in players:
        baselines = {b.metric: b.value for b in player.baselines}
        proe = baselines.get("proe", 0)
        weather = (
            session.query(Weather).filter_by(game_id=f"{week}-{player.id}").first()
        )
        waf = weather.waf if weather else 1.0
        categories, points, variance = project_offense(baselines, proe, waf)
        session.merge(
            Projection(
                player_id=player.id,
                week=week,
                projected_points=points,
                variance=variance,
                data=categories,
            )
        )
        count += 1
    session.commit()
    return count


@celery.task
def project_week(week: int) -> int:
    if SessionLocal is None:
        return 0
    session: Session = SessionLocal()
    try:
        return generate_projections(session, week)
    finally:
        session.close()


def waiver_shortlist_sync(
    session: Session, league_id: int, week: int, horizon: int = 1
) -> Dict[int, Any]:
    league = session.query(League).filter_by(id=league_id).first()
    if not league:
        return {}
    result: Dict[int, Any] = {}
    for team in league.teams:
        result[team.id] = compute_waiver_shortlist(session, team.id, week, horizon)
    return result


@celery.task
def waiver_shortlist(league_id: int, week: int, horizon: int = 1) -> Dict[int, Any]:
    if SessionLocal is None:
        return {}
    session: Session = SessionLocal()
    try:
        return waiver_shortlist_sync(session, league_id, week, horizon)
    finally:
        session.close()


# Create a simple FastAPI app for health checks
app = FastAPI()


@app.get("/healthz")
def healthz() -> Dict[str, bool]:
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
