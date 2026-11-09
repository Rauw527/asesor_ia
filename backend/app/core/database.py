"""Engine/session wiring shared by the API and the tests."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, settings

logger = logging.getLogger(__name__)

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def build_engine(config: Settings | None = None) -> Engine:
    """Create an engine, enabling SQLite pragmas or pgvector when applicable."""
    config = config or settings
    url = config.database_url

    if url.startswith("sqlite"):
        db_path = url.replace("sqlite:///", "", 1)
        if db_path not in {"", ":memory:"}:
            Path(db_path).expanduser().parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(
            url,
            echo=config.sql_echo,
            future=True,
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(engine, "connect")
        def _sqlite_pragmas(dbapi_connection, _record):  # pragma: no cover - driver hook
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

        return engine

    return create_engine(url, echo=config.sql_echo, pool_pre_ping=True, future=True)


def get_engine() -> Engine:
    global _engine, _session_factory
    if _engine is None:
        _engine = build_engine()
        _session_factory = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    get_engine()
    assert _session_factory is not None
    return _session_factory


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a scoped session."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def _enable_pgvector(engine: Engine) -> None:
    if engine.dialect.name != "postgresql":
        return
    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        logger.info("pgvector extension is available")
    except Exception:  # pragma: no cover - depends on server privileges
        logger.warning("Could not enable the pgvector extension; continuing without it")


def init_db(engine: Engine | None = None) -> Engine:
    """Create the schema (idempotent) and seed reference data."""
    from app.core.seed import seed_reference_data
    from app.models import Base

    engine = engine or get_engine()
    _enable_pgvector(engine)
    Base.metadata.create_all(bind=engine)

    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with factory() as session:
        seed_reference_data(session, settings)
        session.commit()
    return engine


def reset_engine() -> None:
    """Drop the cached engine (used by the test-suite)."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
