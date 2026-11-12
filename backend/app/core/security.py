"""Password hashing and JWT utilities."""

from __future__ import annotations

import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    """Hash a password with PBKDF2-HMAC-SHA256 (dev-friendly, no extra dep)."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 210_000)
    return f"pbkdf2_sha256$210000${salt.hex()}${dk.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations, salt_hex, dk_hex = hashed_password.split("$")
        # El formato guarda "pbkdf2_sha256" pero hashlib espera solo "sha256"
        hash_name = algorithm.replace("pbkdf2_", "")
        expected = hashlib.pbkdf2_hmac(
            hash_name,
            plain_password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(expected.hex(), dk_hex)
    except Exception:
        return False


def create_access_token(subject: str) -> str:
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return str(payload.get("sub", ""))
    except JWTError:
        return None
