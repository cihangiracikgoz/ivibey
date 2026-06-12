import uuid
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError

from app.db.database import get_db
from app.models.user import User
from app.core.security import decode_token

bearer = HTTPBearer()

def get_current_user(
        creds: HTTPAuthorizationCredentials = Depends(bearer),
        db: Session = Depends(get_db)
    ) -> User:
    try:
        payload = decode_token(creds.credentials)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    user = db.scalar(
        select(User)
        .where(User.id == uuid.UUID(payload["sub"]))
    )

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user