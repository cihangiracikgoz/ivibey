import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

from app.schemas.song import SongRead

class PlaylistRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PlaylistCreate(BaseModel):
    name: str
    image_url: Optional[str] = None

class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    image_url: Optional[str] = None

class PlaylistDetail(PlaylistRead):
    songs: list[SongRead] = []