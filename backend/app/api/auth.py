from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.entities import Notification, User
from app.schemas.main import (
    LoginIn,
    NotificationOut,
    PasswordResetIn,
    RefreshIn,
    RegisterIn,
    TokenPair,
    UserOut,
)
from app.services.auth import authenticate, password_reset_notice, refresh_tokens, register_user, tokens_for

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/register", response_model=TokenPair)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    user = register_user(db, body)
    db.commit()
    db.refresh(user)
    return tokens_for(user)


@router.post("/auth/login", response_model=TokenPair)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = authenticate(db, body.email, body.password)
    return tokens_for(user)


@router.post("/auth/refresh", response_model=TokenPair)
def refresh(body: RefreshIn, db: Session = Depends(get_db)):
    return refresh_tokens(db, body.refresh_token)


@router.post("/auth/password-reset")
def password_reset(body: PasswordResetIn):
    return password_reset_notice(body.email)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/notifications", response_model=list[NotificationOut])
def notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
