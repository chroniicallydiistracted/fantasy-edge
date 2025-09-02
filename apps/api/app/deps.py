from fastapi import Cookie, Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from jose import JWTError, jwt
from typing import Optional
from .models import User
from .security import TokenEncryptionService
from .settings import settings
from .session import SessionManager
from .yahoo_oauth import YahooOAuthClient
from .yahoo_client import YahooFantasyClient

# Security
security = HTTPBearer()

# Database engine and session setup
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_token_encryption_service():
    return TokenEncryptionService(settings.token_crypto_key)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # In a real implementation, we would fetch the user from the database
    # For now, we'll return a placeholder
    return User(id=user_id, email="user@example.com")


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get the current authenticated user from JWT token, return None if not authenticated"""
    if credentials is None:
        return None

    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def get_debug_user(
    debug_user: Optional[str] = Header(None, alias="X-Debug-User"), db: Session = Depends(get_db)
) -> Optional[User]:
    """Get user via debug header if enabled"""
    if not settings.allow_debug_user or not debug_user:
        return None

    try:
        user_id = int(debug_user)
        # Placeholder user lookup
        return User(id=user_id, email=f"user{user_id}@example.com")
    except ValueError:
        return None


def get_current_user_session(
    session_token: Optional[str] = Cookie(None, alias=SessionManager.COOKIE_NAME),
    db: Session = Depends(get_db),
) -> User:
    """Resolve user from session cookie"""
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = SessionManager.verify_token(session_token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def get_yahoo_client(
    encryption: TokenEncryptionService = Depends(get_token_encryption_service),
) -> YahooFantasyClient:
    oauth = YahooOAuthClient(encryption)
    return YahooFantasyClient(oauth)
