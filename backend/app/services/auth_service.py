import hashlib
import base64
import secrets
import urllib.parse

import httpx
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.cache.redis import store_pkce_verifier, get_pkce_verifier
from app.models.user import User
from app.models.spotify_token import SpotifyToken
from app.core.security import encrypt

def build_authorise_url() -> dict:
    code_verifier = secrets.token_urlsafe(96)
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    state = secrets.token_urlsafe(32)
    store_pkce_verifier(state, code_verifier)

    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "state": state,
        "scope": "user-read-email user-read-private",
        "code_challenge_method": "S256",
        "code_challenge": code_challenge
    }

    url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"

    return {"authorize_url": url, "state": state}

def exchange_code(code: str, state: str) -> dict:
    code_verifier = get_pkce_verifier(state)

    if not code_verifier:
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    
    res = httpx.post(
        "https://accounts.spotify.com/api/token",
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
            "code_verifier": code_verifier
        },
    )

    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Token exchange failed")
    
    return res.json()

def fetch_spotify_profile(access_token: str) -> dict:
    res = httpx.get(
        "https://api.spotify.com/v1/me",
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
    )

    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch profile")
    
    return res.json()

def upsert_user_and_tokens(db: Session, spotify_profile: dict, token_response: dict) -> User:
    user = db.scalar(
        select(User)
        .where(User.spotify_id == spotify_profile["id"])
    )

    if not user:
        user = User(
            spotify_id = spotify_profile["id"], 
            display_name = spotify_profile["display_name"]
        )
        db.add(user)
        db.flush()
    else:
        user.display_name = spotify_profile["display_name"]

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_response["expires_in"])

    token = db.scalar(
        select(SpotifyToken)
        .where(SpotifyToken.user_id == user.id)
    )

    if not token:
        db.add(
            SpotifyToken(
                user_id = user.id,
                access_token = encrypt(token_response["access_token"]),
                refresh_token = encrypt(token_response["refresh_token"]),
                expires_at = expires_at,
                scope = token_response.get("scope"),
                token_type = token_response.get("token_type", "Bearer"),
            )
        )
    else:
        token.access_token = encrypt(token_response["access_token"])
        token.refresh_token = encrypt(token_response["refresh_token"])
        token.expires_at = expires_at
        token.scope = token_response.get("scope")
        token.token_type = token_response.get("token_type", "Bearer")

    db.commit()
    db.refresh(user)
    return user