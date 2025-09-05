from datetime import datetime, timedelta, UTC
from typing import Optional, Literal, Any, cast
from jose import JWTError, jwt
from fastapi import Response
from .settings import settings


class SessionManager:
    """Manages user sessions with JWT tokens stored in cookies"""

    # Use canonical cookie name from settings so all codepaths agree
    COOKIE_NAME = settings.session_cookie_name

    @staticmethod
    def create_token(user_id: int) -> str:
        """Create a JWT token for the user"""
        data: dict[str, Any] = {"sub": str(user_id)}
        expires = datetime.now(UTC) + timedelta(days=7)  # 7-day expiry
        data["exp"] = expires
        return jwt.encode(data, settings.jwt_secret, algorithm="HS256")

    @staticmethod
    def set_session_cookie(response: Response, user_id: int) -> None:
        """Set the session cookie in the response"""
        token = SessionManager.create_token(user_id)
        secure = not settings.allow_debug_user
        raw_samesite = "None" if secure else "Lax"
        response.set_cookie(
            key=SessionManager.COOKIE_NAME,
            value=token,
            httponly=True,
            samesite=cast(Literal["lax", "strict", "none"], raw_samesite),
            secure=secure,
            max_age=60 * 60 * 24 * 7,
        )

    @staticmethod
    def clear_session_cookie(response: Response) -> None:
        """Clear the session cookie"""
        response.delete_cookie(SessionManager.COOKIE_NAME)

    @staticmethod
    def verify_token(token: str) -> Optional[int]:
        """Verify a JWT token and return the user ID"""
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
            sub = payload.get("sub")
            if sub is None:
                return None
            user_id = int(sub)
            return user_id
        except (JWTError, ValueError, TypeError):
            return None
