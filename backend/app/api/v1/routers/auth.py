"""Auth endpoints: register, login, me."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import UserLogin, UserOut, UserRegister
from app.services.auth_service import login, register

router = APIRouter(tags=["auth"])


@router.post(
    "/auth/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registro de usuario",
)
def register_user(payload: UserRegister, db: Session = Depends(get_db)) -> UserOut:
    return register(db, payload)


@router.post("/auth/login", summary="Inicio de sesión")
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    return login(db, payload)


@router.get("/auth/me", response_model=UserOut, summary="Usuario autenticado")
def get_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
