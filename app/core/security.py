from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


# ---------- Passwords ----------
def hash_password(password: str) -> str:
    """Turn a plain password into a salted bcrypt hash, safe to store."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Check a plain password against a stored hash. Bad/placeholder hashes return False, not a crash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


# ---------- JWT tokens ----------
def create_access_token(data: dict, expires_minutes: int | None = None) -> str:
    """Create a signed token that proves who a user is."""
    to_encode = data.copy()
    minutes = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Verify a token's signature and expiry. Returns the data, or None if invalid."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        return None