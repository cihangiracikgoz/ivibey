import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from app.db.database import Base

from sqlalchemy import DateTime, String, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.playlist import Playlist

class Song(Base):
    __tablename__ = "songs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spotify_track_id: Mapped[str] = mapped_column(String(255), nullable=False)
    playlist_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    playlist: Mapped["Playlist"] = relationship(back_populates="songs")

    def __repr__(self) -> str:
        return f"<Song(id={self.id}, spotify_track_id={self.spotify_track_id}, playlist_id={self.playlist_id}, name='{self.name}', position={self.position})>"
