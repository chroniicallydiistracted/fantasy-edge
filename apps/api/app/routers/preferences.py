from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any

from ..deps import get_db, get_current_user_session
from ..models import UserPreferences

router = APIRouter()


class PreferencesUpdate(BaseModel):
    theme: str
    saved_views: Dict[str, Any]
    pinned_players: List[int]


@router.get("/")
def get_preferences(db: Session = Depends(get_db), current_user=Depends(get_current_user_session)):
    """Get user preferences"""
    preferences = (
        db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    )
    if not preferences:
        # Return default preferences if none exist
        return {"theme": "system", "saved_views": {}, "pinned_players": []}
    return {
        "theme": preferences.theme,
        "saved_views": preferences.saved_views,
        "pinned_players": preferences.pinned_players,
    }


@router.put("/")
def update_preferences(
    preferences: PreferencesUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_session),
):
    """Update user preferences"""
    # Get or create preferences
    pref = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()

    if not pref:
        pref = UserPreferences(
            user_id=current_user.id,
            theme=preferences.theme,
            saved_views=preferences.saved_views,
            pinned_players=preferences.pinned_players,
        )
        db.add(pref)
    else:
        pref.theme = preferences.theme
        pref.saved_views = preferences.saved_views
        pref.pinned_players = preferences.pinned_players

    db.commit()
    return {"message": "Preferences updated successfully"}
