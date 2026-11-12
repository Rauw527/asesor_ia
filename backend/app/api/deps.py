"""FastAPI dependency providers.

Singletons are created lazily so the API can boot (and `/health` can answer)
without a Gemini key, Redis or PostgreSQL.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db  # re-exported for routers
from app.models.user import User
from app.repositories import user_repository
from app.services.cache import CacheBackend, build_cache
from app.services.gemini_service import GeminiService, build_gemini_service
from app.services.storage import LocalStorage

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

_gemini: GeminiService | None = None
_cache: CacheBackend | None = None
_storage: LocalStorage | None = None


def get_gemini() -> GeminiService:
    global _gemini
    if _gemini is None:
        _gemini = build_gemini_service(get_settings())
    return _gemini


def get_cache() -> CacheBackend:
    global _cache
    if _cache is None:
        _cache = build_cache(get_settings())
    return _cache


def get_storage() -> LocalStorage:
    global _storage
    if _storage is None:
        settings = get_settings()
        _storage = LocalStorage(
            root=settings.storage_dir,
            url_prefix=f"{settings.api_v1_prefix}/media",
        )
    return _storage


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user from the Bearer JWT."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    from app.core.security import decode_token

    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = user_repository.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    return user


def reset_singletons() -> None:
    """Test hook: drop cached adapters."""
    global _gemini, _cache, _storage
    _gemini = None
    _cache = None
    _storage = None


__all__ = [
    "get_cache",
    "get_current_user",
    "get_db",
    "get_gemini",
    "get_storage",
    "oauth2_scheme",
    "reset_singletons",
]
