"""FastAPI application factory."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import init_db
from app.core.exceptions import DomainError
from app.services.gemini_service import GeminiError

logger = logging.getLogger(__name__)


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
    )


def create_app() -> FastAPI:
    config = get_settings()
    _configure_logging(config.log_level)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        engine = init_db()
        logger.info(
            "Database ready (%s) | model=%s | gemini=%s",
            engine.dialect.name,
            config.gemini_model,
            "configured" if config.gemini_enabled else "MISSING API KEY",
        )
        yield

    app = FastAPI(
        title=config.app_name,
        version=config.app_version,
        description=(
            "Phase 1 — Skincare: diagnóstico facial, auditoría INCI y tracker "
            "de evolución mensual con Gemini Vision."
        ),
        lifespan=lifespan,
    )

    wildcard = "*" in config.cors_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        # Browsers reject wildcard origins combined with credentials.
        allow_credentials=not wildcard,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DomainError)
    async def _domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(GeminiError)
    async def _gemini_error_handler(_request: Request, exc: GeminiError) -> JSONResponse:
        code = "ai_unavailable" if exc.status_code == 503 else "ai_error"
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": code},
        )

    app.include_router(api_router, prefix=config.api_v1_prefix)

    media_dir = config.storage_dir
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount(
        f"{config.api_v1_prefix}/media",
        StaticFiles(directory=media_dir),
        name="media",
    )

    def _health() -> dict[str, Any]:
        return {
            "status": "ok",
            "version": config.app_version,
            "environment": config.environment,
            "gemini_configured": config.gemini_enabled,
            "gemini_model": config.gemini_model,
            "database": "sqlite" if config.is_sqlite else "postgresql",
        }

    app.add_api_route("/health", _health, tags=["health"], include_in_schema=True)
    app.add_api_route(
        f"{config.api_v1_prefix}/health",
        _health,
        tags=["health"],
        include_in_schema=False,
    )

    return app


app = create_app()
