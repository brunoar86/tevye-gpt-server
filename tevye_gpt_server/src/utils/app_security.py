import os
import uuid
import hashlib
import secrets

from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Any, Dict, List, Tuple
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone


JWT_SECRET = os.getenv("SECRET")
REFRESH_SECRET = os.getenv("SECRET")
JWT_ALG = os.getenv("JWT_ALGORITHM")

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
        "tv": token_version,
        "iat": int(now.timestamp()),
        "exp": int((now + ACCESS_TTL).timestamp()),
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError as e:
        raise ValueError("Invalid or expired access token") from e


def make_refresh_token(*, sub: str, sid: str) -> Tuple[str, Dict[str, Any]]:
    jti = uuid.uuid4()
    rnd = secrets.token_urlsafe(32)
    token = f"{jti}.{rnd}"
    meta: Dict[str, Any] = {"jti": jti, "sub": sub, "sid": sid}
    return token, meta


def hash_refresh(refresh_token: str) -> str:
    return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()


def verify_jwt_from_request(request) -> dict:
    """
    Validate JWT from Authorization header in the request.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        # Aqui o senhor pode validar iss, aud, roles, etc.
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e
