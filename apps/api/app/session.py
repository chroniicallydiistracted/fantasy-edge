from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Response
from .settings import settings

class SessionManager:
    """Manages user sessions with JWT tokens stored in cookies"""

    COOKIE_NAME = "fe_session"

    @staticmethod
    def create_token(user_id: int) -> str:
        """Create a JWT token for the user"""
        data = {"sub": str(user_id)}
        expires = datetime.utcnow() + timedelta(days=7)  # 7-day expiry
        data.update({"exp": expires})
        return jwt.encode(data, settings.session_secret, algorithm="HS256")

    @staticmethod
    def set_session_cookie(response: Response, user_id: int) -> None:
        """Set the session cookie in the response"""
        token = SessionManager.create_token(user_id)
        response.set_cookie(
            key=SessionManager.COOKIE_NAME,
            value=token,
            httponly=True,  # Not accessible from JavaScript
            samesite="Lax",  # CSRF protection
            secure=False,  # Set to True in production
            max_age=60 * 60 * 24 * 7,  # 7 days in seconds
        )

    @staticmethod
    def clear_session_cookie(response: Response) -> None:
        """Clear the session cookie"""
        response.delete_cookie(SessionManager.COOKIE_NAME)

    @staticmethod
    def verify_token(token: str) -> Optional[int]:
        """Verify a JWT token and return the user ID"""
        try:
            payload = jwt.decode(token, settings.session_secret, algorithms=["HS256"])
            user_id = int(payload.get("sub"))
            return user_id
        except (JWTError, ValueError):
            return None
