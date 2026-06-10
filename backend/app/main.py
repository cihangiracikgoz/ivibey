from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import engine
from app.api.v1.router import router as v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()

app = FastAPI(title="iVibey API", version="1.0.0", lifespan=lifespan)
app.include_router(v1_router)

@app.get("/")
def health_check():
    return {"message": "iVibey API is running!"}