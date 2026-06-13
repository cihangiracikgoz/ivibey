from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.services import spotify_service
from app.api.dependency import get_current_user
from app.db.database import get_db
from app.models.user import User

router = APIRouter(prefix="/spotify", tags=["spotify"])

@router.get("/search")
def search(
    q: str,
    limit: int = Query(default=10, ge=1, le=10),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return spotify_service.search_tracks(db, user, q, limit)