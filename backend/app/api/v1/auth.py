import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.auth import Token, TokenRefresh
from app.services import auth_service
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.db.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
def login():
    return auth_service.build_authorise_url()

@router.get("/callback", response_model=Token)
def callback(code: str, state: str, db: Session = Depends(get_db)):
    res = auth_service.exchange_code(code, state)
    profile = auth_service.fetch_spotify_profile(res["access_token"])
    user = auth_service.upsert_user_and_tokens(db, profile, res)

    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )

@router.post("/refresh", response_model=Token)
def refresh(body: TokenRefresh):
    payload = decode_token(body.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Invalid token type")
    
    user_id = uuid.UUID(payload["sub"])
    return Token(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id)
    )