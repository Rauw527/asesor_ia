"""Aggregated v1 router."""

from fastapi import APIRouter

from app.api.v1.routers import (
    analysis,
    auth,
    catalog_ingredients,
    catalog_products,
    consents,
    inci,
    photos,
    questionnaires,
    recommendations,
    routine,
    skin,
    skin_profiles,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(skin.router)
api_router.include_router(inci.router)
api_router.include_router(routine.router)
api_router.include_router(consents.router)
api_router.include_router(photos.router)
api_router.include_router(questionnaires.router)
api_router.include_router(analysis.router)
api_router.include_router(skin_profiles.router)
api_router.include_router(recommendations.router)
api_router.include_router(catalog_products.router)
api_router.include_router(catalog_ingredients.router)

__all__ = ["api_router"]
