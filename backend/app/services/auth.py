from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import conflict, unauthorized
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.models.entities import (
    BusinessProfile,
    CollectorProfile,
    ConsumerProfile,
    RecyclerProfile,
    Role,
    User,
)
from app.schemas.main import TokenPair
from app.services.system import audit


def tokens_for(user: User) -> TokenPair:
    return TokenPair(access_token=create_access_token(user.id), refresh_token=create_refresh_token(user.id))


def register_user(db: Session, data) -> User:
    if db.query(User).filter(User.email == data.email.lower()).first():
        raise conflict("Email already registered")
    user = User(
        email=data.email.lower(),
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        role=data.role,
    )
    db.add(user)
    db.flush()
    if data.role == Role.CONSUMER:
        db.add(ConsumerProfile(user_id=user.id, area="Whitefield"))
    elif data.role == Role.COLLECTOR:
        db.add(CollectorProfile(user_id=user.id, service_areas=["Whitefield"], accepted_materials=["copper", "aluminium"]))
    elif data.role == Role.RECYCLER:
        db.add(
            RecyclerProfile(
                user_id=user.id,
                organization_name=data.organization_name or data.full_name,
                location="Bengaluru",
            )
        )
    elif data.role == Role.BUSINESS:
        db.add(
            BusinessProfile(
                user_id=user.id,
                organization_name=data.organization_name or data.full_name,
                organization_type=data.organization_type or "IT company",
            )
        )
    audit(db, "auth.register", "user", str(user.id), user.id, {"role": user.role.value})
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user or not verify_password(password, user.hashed_password):
        raise unauthorized("Invalid email or password")
    if not user.is_active:
        raise unauthorized("Account inactive")
    return user


def refresh_tokens(db: Session, refresh_token: str) -> TokenPair:
    raw = decode_token(refresh_token, "refresh")
    if not raw:
        raise unauthorized("Invalid refresh token")
    user = db.get(User, UUID(raw))
    if not user:
        raise unauthorized("Invalid refresh token")
    return tokens_for(user)


def password_reset_notice(email: str) -> dict:
    return {
        "message": "If an account exists for that email, a reset link would be sent. Email delivery is not configured yet.",
        "email": email,
        "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
    }
