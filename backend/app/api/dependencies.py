from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import verify_token


def get_current_user(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """Validate Bearer token and return active user."""
    if not authorization:
        raise AppError("Authentication credentials were not provided", status_code=401)

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AppError("Invalid authorization scheme. Expected 'Bearer <token>'", status_code=401)

    token = parts[1]
    payload = verify_token(token)
    username = payload.get("username")
    if not username:
        raise AppError("Malformed token payload", status_code=401)

    user = UserRepository.get_by_username(db, username)
    if not user:
        raise AppError("User associated with token not found", status_code=401)
    if not user.is_active:
        raise AppError("User account is inactive", status_code=403)

    return user


def require_staff(current_user: User = Depends(get_current_user)) -> User:
    """Verify that current user is an authorized canteen staff member or admin."""
    if current_user.role not in ("staff", "admin"):
        raise AppError("Access denied: staff privileges required", status_code=403)
    return current_user


__all__ = ["get_db", "get_current_user", "require_staff"]
from app.models.enums import UserRole
from app.repositories.user_repository import UserRepository

def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    """Prototype bearer format: Bearer demo-user-<id>. Replace with real tokens later."""
    if not authorization or not authorization.startswith("Bearer demo-user-"):
        raise AppError("Unauthorized", 401)
    try: user_id = int(authorization.removeprefix("Bearer demo-user-"))
    except ValueError: raise AppError("Unauthorized", 401)
    user = UserRepository(db).get_by_id(user_id)
    if not user: raise AppError("Unauthorized", 401)
    return user

def require_admin(user=Depends(get_current_user)):
    if user.role != UserRole.ADMIN: raise AppError("Forbidden", 403)
    return user

__all__ = ["get_db", "get_current_user", "require_admin"]
