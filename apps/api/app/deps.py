from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from .models import User
from .security import TokenEncryptionService
from .settings import settings

# Security
security = HTTPBearer()

def get_db():
    # This would normally come from a session manager
    # For now, we'll implement a placeholder
    pass

def get_token_encryption_service():
    return TokenEncryptionService(settings.token_crypto_key)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(
            credentials.credentials, 
            settings.session_secret, 
            algorithms=["HS256"]
        )
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
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get the current authenticated user from JWT token, return None if not authenticated"""
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

def get_debug_user(
    authorization: str = None,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get user via debug header if enabled"""
    if not settings.allow_debug_user:
        return None
    
    # Extract debug header
    if authorization and authorization.startswith("X-Debug-User: "):
        try:
            user_id = int(authorization.split("X-Debug-User: ")[1])
            # In a real implementation, we would fetch the user from the database
            # For now, we'll return a placeholder
            return User(id=user_id, email=f"user{user_id}@example.com")
        except (ValueError, IndexError):
            pass
    
    return None
