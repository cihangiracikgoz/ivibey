import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.playlist import PlaylistRead, PlaylistCreate, PlaylistUpdate, PlaylistDetail
from app.services import playlist_service
from app.api.dependency import get_current_user
from app.db.database import get_db
from app.models.user import User

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.get("/", response_model=list[PlaylistRead])
def list_playlists(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return playlist_service.list_playlists(db, user.id)


@router.post("/", response_model=PlaylistRead, status_code=status.HTTP_201_CREATED)
def create_playlist(data: PlaylistCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return playlist_service.create_playlist(db, user.id, data)


@router.get("/{playlist_id}", response_model=PlaylistDetail)
def get_playlist(playlist_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return playlist_service.get_playlist(db, playlist_id, user.id)


@router.patch("/{playlist_id}", response_model=PlaylistRead)
def update_playlist(playlist_id: uuid.UUID, data: PlaylistUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return playlist_service.update_playlist(db, playlist_id, user.id, data)


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playlist(playlist_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    playlist_service.delete_playlist(db, playlist_id, user.id)
