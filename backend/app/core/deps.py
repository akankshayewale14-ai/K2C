from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.errors import forbidden, unauthorized
from app.core.security import decode_token
from app.db.session import get_db
from app.models.entities import Role, User


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise unauthorized()
    raw = decode_token(authorization.split(" ", 1)[1], "access")
    if not raw:
        raise unauthorized("Invalid or expired token")
    try:
        user_id = UUID(raw)
    except ValueError:
        raise unauthorized("Invalid or expired token")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise unauthorized("Account inactive")
    return user


def require_roles(*roles: Role):
    def _inner(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles and user.role != Role.ADMIN:
            raise forbidden("Insufficient role")
        return user

    return _inner
