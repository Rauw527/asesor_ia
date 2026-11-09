"""Authentication: register, login, token."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth import UserLogin, UserOut, UserRegister


def register(db, payload: UserRegister) -> UserOut:
    existing = user_repository.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )

    user = user_repository.create_user(
        db,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    db.commit()
    return UserOut.model_validate(user)


def authenticate(db, payload: UserLogin) -> User:
    user = user_repository.get_user_by_email(db, payload.email)
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    return user


def login(db, payload: UserLogin) -> dict:
    user = authenticate(db, payload)
    token = create_access_token(subject=user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.model_validate(user),
    }


def get_current_user_id_from_token(token: str) -> str | None:
    from app.core.security import decode_token

    return decode_token(token)
