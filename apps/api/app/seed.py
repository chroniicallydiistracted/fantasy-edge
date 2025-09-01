from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import League


def seed_league(db: Session, yahoo_id: int = 528886, name: str | None = None) -> League:
    """Ensure a league row exists for the given Yahoo league id."""
    league = db.execute(select(League).where(League.yahoo_id == yahoo_id)).scalar_one_or_none()
    if league is None:
        league = League(yahoo_id=yahoo_id, name=name or f"League {yahoo_id}")
        db.add(league)
        db.commit()
        db.refresh(league)
    return league
