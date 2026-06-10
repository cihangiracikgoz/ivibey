import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.song import Song
from app.schemas.song import SongCreate, SongUpdate
from app.services.playlist_service import get_playlist


def get_song(db: Session, playlist_id: uuid.UUID, song_id: uuid.UUID, user_id: uuid.UUID) -> Song:
    get_playlist(db, playlist_id, user_id)

    song = db.scalar(
        select(Song)
        .where(Song.id == song_id, Song.playlist_id == playlist_id)
    )
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
    return song


def list_songs(db: Session, playlist_id: uuid.UUID, user_id: uuid.UUID) -> list[Song]:
    get_playlist(db, playlist_id, user_id)

    return list(db.scalars(
        select(Song)
        .where(Song.playlist_id == playlist_id)
        .order_by(Song.position.asc())
    ).all())
    

def add_song(db: Session, playlist_id: uuid.UUID, user_id: uuid.UUID, data: SongCreate) -> Song:
    get_playlist(db, playlist_id, user_id)

    song = Song(**data.model_dump(), playlist_id=playlist_id)
    db.add(song)
    db.commit()
    db.refresh(song)
    return song


def update_song(db: Session, playlist_id: uuid.UUID, song_id: uuid.UUID, user_id: uuid.UUID, data: SongUpdate) -> Song:
    song = get_song(db, playlist_id, song_id, user_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(song, field, value)

    db.commit()
    db.refresh(song)
    return song


def delete_song(db: Session, playlist_id: uuid.UUID, song_id: uuid.UUID, user_id: uuid.UUID) -> None:
    song = get_song(db, playlist_id, song_id, user_id)

    db.delete(song)
    db.commit()