import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Optional

class SongRead(BaseModel):
    id: uuid.UUID
    spotify_track_id: str
    playlist_id: uuid.UUID
    name: str
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SongCreate(BaseModel):
    spotify_track_id: str
    name: str
    position: int

class SongUpdate(BaseModel):
    spotify_track_id: Optional[str] = None
    name: Optional[str] = None
    position: Optional[int] = None