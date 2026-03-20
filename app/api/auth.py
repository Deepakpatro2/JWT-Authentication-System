from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    ChangePasswordRequest,
    TokenResponse,
    AccessTokenResponse,
    UserPublic,
    MessageResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.
    - Validates name, email format, password strength
    - Hashes password with bcrypt
    - Returns access_token (30 min) + refresh_token (7 days)
    """
    result = auth_service.register_user(db, req)
    return result


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email + password.
    - Uses bcrypt constant-time comparison
    - Rotates refresh token on each login
    - Returns access_token + refresh_token
    """
    result = auth_service.login_user(db, req)
    return result


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(req: RefreshRequest, db: Session = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access token.
    - Implements refresh token rotation (old token invalidated)
    - Detects token reuse (possible theft) and rejects it
    """
    result = auth_service.refresh_access_token(db, req.refresh_token)
    return result


@router.post("/logout", response_model=MessageResponse)
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Revoke the user's refresh token server-side.
    Client should also delete the token from storage.
    """
    auth_service.logout_user(db, current_user)
    return {"message": "Logged out successfully"}


@router.get("/profile", response_model=UserPublic)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Protected route — requires valid JWT.
    Returns the authenticated user's profile.
    """
    return current_user


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change password for authenticated user.
    Forces re-login by revoking refresh token.
    """
    auth_service.change_password(db, current_user, req.current_password, req.new_password)
    return {"message": "Password changed. Please log in again."}
