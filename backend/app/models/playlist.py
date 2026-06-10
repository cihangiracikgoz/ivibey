import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.db.database import Base

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.song import Song

class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    songs: Mapped[list["Song"]] = relationship(back_populates="playlist", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self) -> str:
        return f"<Playlist(id={self.id}, user_id={self.user_id}, name='{self.name}', image_url='{self.image_url}', created_at={self.created_at}, updated_at={self.updated_at})>"
