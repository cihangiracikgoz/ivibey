from fastapi import APIRouter
from app.api.v1.playlists import router as playlists_router
from app.api.v1.songs import router as songs_router
from app.api.v1.auth import router as auth_router

router = APIRouter(prefix="/api/v1")
router.include_router(playlists_router)
router.include_router(songs_router)
router.include_router(auth_router)