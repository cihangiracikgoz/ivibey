import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.playlist import Playlist
from app.schemas.playlist import PlaylistCreate, PlaylistUpdate


def get_playlist(db: Session, playlist_id: uuid.UUID, user_id: uuid.UUID) -> Playlist:
    playlist = db.scalar(
        select(Playlist)
        .where(Playlist.id == playlist_id, Playlist.user_id == user_id)
    )
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    return playlist


def list_playlists(db: Session, user_id: uuid.UUID) -> list[Playlist]:
    return list(db.scalars(
        select(Playlist)
        .where(Playlist.user_id == user_id)
        .order_by(Playlist.created_at.desc())
    ).all())


def create_playlist(db: Session, user_id: uuid.UUID, data: PlaylistCreate) -> Playlist:
    playlist = Playlist(**data.model_dump(), user_id=user_id)
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist


def update_playlist(db: Session, playlist_id: uuid.UUID, user_id: uuid.UUID, data: PlaylistUpdate) -> Playlist:
    playlist = get_playlist(db, playlist_id, user_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(playlist, field, value)

    db.commit()
    db.refresh(playlist)
    return playlist


def delete_playlist(db: Session, playlist_id: uuid.UUID, user_id: uuid.UUID) -> None:
    playlist = get_playlist(db, playlist_id, user_id)
    db.delete(playlist)
    db.commit()
