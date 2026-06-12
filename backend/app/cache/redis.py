import redis
from app.core.config import settings

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)

def store_pkce_verifier(state: str, code_verifier: str):
    r.setex(f"pkce:{state}", 600, code_verifier)

def get_pkce_verifier(state: str) -> str | None:
    return r.getdel(f"pkce:{state}")