"""User persistence helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.models import User


def get_user(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_or_create_demo_user(db: Session, config: Settings) -> User:
    user = get_user_by_email(db, config.demo_user_email)
    if user is None:
        user = User(email=config.demo_user_email, full_name=config.demo_user_name)
        db.add(user)
        db.flush()
    return user


def resolve_user(db: Session, user_id: str | None, config: Settings) -> User:
    """Return the requested user or the demo identity (no auth in Phase 1)."""
    if not user_id:
        return get_or_create_demo_user(db, config)

    user = get_user(db, user_id)
    if user is None:
        raise NotFoundError(f"No existe el usuario '{user_id}'.")
    return user


def create_user(
    db: Session,
    email: str,
    full_name: str,
    password_hash: str | None = None,
) -> User:
    user = User(email=email, full_name=full_name, password_hash=password_hash)
    db.add(user)
    db.flush()
    return user
