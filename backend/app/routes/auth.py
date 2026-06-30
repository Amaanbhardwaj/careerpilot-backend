import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, GoogleLoginRequest, LoginRequest, RegisterRequest, UserResponse
from app.services.auth_service import create_access_token, get_current_user, hash_password, verify_password


router = APIRouter(prefix="/auth")


def _auth_response(user: User) -> AuthResponse:
    return AuthResponse(access_token=create_access_token(user), user=UserResponse.model_validate(user))


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    existing_user = db.execute(select(User).where(User.email == payload.email.lower())).scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        auth_provider="local",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.execute(select(User).where(User.email == payload.email.lower())).scalars().first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    return _auth_response(user)


@router.post("/google", response_model=AuthResponse)
async def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google login is not configured. Add GOOGLE_CLIENT_ID in .env.",
        )

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": payload.id_token},
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token verification failed.",
        )

    profile = response.json()
    if profile.get("aud") != settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token audience does not match this app.",
        )

    email = profile["email"].lower()
    user = db.execute(select(User).where(User.email == email)).scalars().first()
    if not user:
        user = User(
            full_name=profile.get("name") or email.split("@")[0],
            email=email,
            password_hash=None,
            auth_provider="google",
            google_sub=profile.get("sub"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return _auth_response(user)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get("/config")
def auth_config() -> dict[str, str]:
    return {"google_client_id": settings.google_client_id}
