from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Turn a bearer token into the logged-in User, or reject the request."""
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.get(User, payload.get("user_id"))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_roles(*roles: str):
    """Dependency factory: only allow users whose role is in `roles`."""
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role.value not in roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return checker