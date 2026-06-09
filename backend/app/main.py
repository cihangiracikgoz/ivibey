from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()

app = FastAPI(title="iVibey API", version="1.0.0", lifespan=lifespan)

@app.get("/")
def health_check():
    return {"message": "iVibey API is running!"}