"""JWT token generation and verification service."""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def create_token(user_id: UUID, email: str, secret_key: str) -> str:
    """
    Create a JWT token for authenticated user.
    
    Args:
        user_id: User's unique identifier
        email: User's email address
        secret_key: Secret key for signing the token (BETTER_AUTH_SECRET)
        
    Returns:
        Encoded JWT token string
    """
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(payload, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, secret_key: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify
        secret_key: Secret key for verifying the token (BETTER_AUTH_SECRET)
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def extract_user_id(token: str, secret_key: str) -> Optional[UUID]:
    """
    Extract user_id from a JWT token.
    
    Args:
        token: JWT token string
        secret_key: Secret key for verifying the token
        
    Returns:
        User UUID if token is valid, None otherwise
    """
    payload = verify_token(token, secret_key)
    if payload is None:
        return None
    
    try:
        user_id = UUID(payload.get("user_id"))
        return user_id
    except (ValueError, TypeError):
        return None
