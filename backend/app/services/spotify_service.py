import httpx
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.config import settings
from app.models.spotify_token import SpotifyToken
from app.core.security import decrypt, encrypt

def refresh_spotify_token(db: Session, token: SpotifyToken) -> str:
    decrypted = decrypt(token.refresh_token)

    res = httpx.post(
        "https://accounts.spotify.com/api/token",
        data = {
            "grant_type": "refresh_token",
            "refresh_token": decrypted,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET
        }
    )

    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="Token refresh failed")

    data =  res.json()

    token.access_token= encrypt(data["access_token"])
    if "refresh_token" in data:
        token.refresh_token = encrypt(data["refresh_token"])
    token.expires_at = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"])
    token.scope = data.get("scope", token.scope)

    db.commit()
    return data["access_token"]


def get_valid_access_token(db: Session, user: User) -> str:
    token = db.scalar(
        select(SpotifyToken)
        .where(SpotifyToken.user_id == user.id)
    )

    if not token:
        raise HTTPException(status_code=401, detail="No Spotify token found")
    
    if token.expires_at <= datetime.now(timezone.utc) + timedelta(seconds=120):
        return refresh_spotify_token(db, token)
    
    return decrypt(token.access_token)

def spotify_request(db: Session, user: User, method: str, path: str, **kwargs) -> dict:
    access_token = get_valid_access_token(db, user)

    res = httpx.request(
        method,
        url = f"https://api.spotify.com/v1{path}",
        headers = {
            "Authorization": f"Bearer {access_token}"
        },
        **kwargs,
    )

    if res.status_code == 401:
        token = db.scalar(
            select(SpotifyToken)
            .where(SpotifyToken.user_id == user.id)
        )
        access_token = refresh_spotify_token(db, token)
        res = httpx.request(
            method,
            url= f"https://api.spotify.com/v1{path}",
            headers= {
                "Authorization": f"Bearer {access_token}"
            },
            **kwargs,
        )

    if res.status_code >= 400:
        raise HTTPException(status_code=res.status_code, detail="Spotify API error")
    
    return res.json()

def search_tracks(db: Session, user: User, query: str, limit: int = 20) -> list[dict]:
    data = spotify_request(
        db, user, "GET", "/search",
        params = {
            "q": query,
            "type": "track",
            "limit": limit
        }
    )

    return [
        {
            "spotify_track_id": t["id"],
            "name": t["name"],
            "artist": ", ".join(a["name"] for a in t["artists"]),
            "duration_ms": t["duration_ms"],
            "image_url": t["album"]["images"][0]["url"] if t["album"]["images"] else None,
        }
        for t in data["tracks"]["items"]
    ]