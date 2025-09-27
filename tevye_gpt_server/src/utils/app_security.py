import hashlib
import uuid
import secrets

from jose import jwt
from passlib.context import CryptContext
from typing import Any, Dict, List, Tuple
from datetime import datetime, timedelta, timezone


JWT_SECRET = "change-me-access-secret"
REFRESH_SECRET = "change-me-refresh-secret"
JWT_ALG = "HS256"

ACCESS_TTL = timedelta(minutes=15)
REFRESH_TTL = timedelta(days=30)

__all__ = [
    "hash_password", "verify_password", "make_access_token",
    "make_refresh_token", "hash_refresh", "REFRESH_TTL", "ACCESS_TTL"
]

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt_sha256", "bcrypt"],
    deprecated="auto"
)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def make_access_token(
    *,
    sub: str,
    sid: str,
    roles: List[str],
    token_version: int
) -> str:
    now = _utcnow()
    payload = {
        "sub": sub,
        "sid": sid,
        "roles": roles,
        "tv": token_version,         # token version
        "iat": int(now.timestamp()),
        "exp": int((now + ACCESS_TTL).timestamp()),
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def make_refresh_token(*, sub: str, sid: str) -> Tuple[str, Dict[str, Any]]:
    jti = uuid.uuid4()
    rnd = secrets.token_urlsafe(32)
    token = f"{jti}.{rnd}"
    meta = {"jti": jti, "sub": sub, "sid": sid}
    return token, meta


def hash_refresh(refresh_token: str) -> str:
    # Store only this hash in DB
    return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
