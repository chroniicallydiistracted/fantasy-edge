from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, UTC

from ..deps import get_db, get_current_user_session
from ..models import EventLog

router = APIRouter()


@router.get("/")
def get_events(
    since: Optional[datetime] = Query(None, description="Get events since this timestamp"),
    limit: int = Query(100, description="Maximum number of events to return"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_session),
):
    """Get event log entries, optionally filtered by timestamp"""
    query = db.query(EventLog).order_by(EventLog.ts.desc())

    if since is not None:
        if since.tzinfo is None:
            since = since.replace(tzinfo=UTC)
        query = query.filter(EventLog.ts >= since)

    events = query.limit(limit).all()
    return events
