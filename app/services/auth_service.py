from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import JWTError

from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import get_settings
from app.schemas.auth import RegisterRequest, LoginRequest

settings = get_settings()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def register_user(db: Session, req: RegisterRequest) -> dict:
    """
    Create new user. Raises 409 if email taken.
    Returns access + refresh tokens.
    """
    if get_user_by_email(db, req.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        name=req.name,
        email=req.email,
        hashed_password=hash_password(req.password),
    )

    refresh_token = create_refresh_token(user.email)
    user.refresh_token = refresh_token

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        subject=user.email,
        extra={"user_id": user.id, "role": user.role},
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user,
    }


def login_user(db: Session, req: LoginRequest) -> dict:
    """
    Authenticate user. Raises 401 on bad credentials.
    Returns access + refresh tokens.
    """
    user = get_user_by_email(db, req.email)

    # Deliberately vague error — never reveal which field is wrong
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    refresh_token = create_refresh_token(user.email)
    user.refresh_token = refresh_token  # rotate on every login
    db.commit()

    access_token = create_access_token(
        subject=user.email,
        extra={"user_id": user.id, "role": user.role},
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user,
    }


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    """
    Validate refresh token, issue a new access token.
    Implements refresh token rotation (old token invalidated).
    """
    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token is invalid or expired")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Wrong token type")

    user = get_user_by_email(db, payload["sub"])
    if not user or user.refresh_token != refresh_token:
        # Token reuse detected — could mean theft
        raise HTTPException(status_code=401, detail="Refresh token already used or revoked")

    # Rotate: issue new refresh token, invalidate old one
    new_refresh = create_refresh_token(user.email)
    user.refresh_token = new_refresh
    db.commit()

    new_access = create_access_token(
        subject=user.email,
        extra={"user_id": user.id, "role": user.role},
    )

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


def logout_user(db: Session, user: User) -> None:
    """Revoke refresh token server-side so it can't be reused."""
    user.refresh_token = None
    db.commit()


def change_password(db: Session, user: User, current_pw: str, new_pw: str) -> None:
    if not verify_password(current_pw, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.hashed_password = hash_password(new_pw)
    user.refresh_token = None  # force re-login after password change
    db.commit()
