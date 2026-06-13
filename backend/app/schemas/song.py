import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Optional

class SongRead(BaseModel):
    id: uuid.UUID
    spotify_track_id: str
    playlist_id: uuid.UUID
    name: str
    artist: str
    duration_ms: int
    image_url: Optional[str] = None
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SongCreate(BaseModel):
    spotify_track_id: str
    name: str
    artist: str
    duration_ms: int
    image_url: Optional[str] = None
    position: int

class SongUpdate(BaseModel):
    position: Optional[int] = None