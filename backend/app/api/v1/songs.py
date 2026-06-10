import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.song import SongRead, SongCreate, SongUpdate
from app.services import song_service
from app.api.dependency import get_current_user
from app.db.database import get_db
from app.models.user import User

router = APIRouter(prefix="/playlists/{playlist_id}/songs", tags=["songs"])

@router.get("/", response_model=list[SongRead])
def get_songs(playlist_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return song_service.list_songs(db, playlist_id, user.id)


@router.post("/", response_model=SongRead, status_code=status.HTTP_201_CREATED)
def add_song(playlist_id: uuid.UUID, data: SongCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return song_service.add_song(db, playlist_id, user.id, data)


@router.patch("/{song_id}", response_model=SongRead)
def update_song(playlist_id: uuid.UUID, song_id: uuid.UUID, data: SongUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return song_service.update_song(db, playlist_id, song_id, user.id, data)


@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_song(playlist_id: uuid.UUID, song_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    song_service.delete_song(db, playlist_id, song_id, user.id)