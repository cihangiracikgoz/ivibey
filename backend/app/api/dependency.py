from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User

DEV_SPOTIFY_ID = 'dev_user_spotify_id'

def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.scalar(
        select(User)
        .where(User.spotify_id == DEV_SPOTIFY_ID)
    )

    if not user:
        user = User(spotify_id=DEV_SPOTIFY_ID, display_name='Dev User')
        db.add(user)
        db.commit()
        db.refresh(user)

    return user