"""Catalog ingredient endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.ingredient import IngredientOut
from app.services.ingredient_service import list_ingredients

router = APIRouter(tags=["catalog-ingredients"])


@router.get(
    "/ingredients",
    response_model=list[IngredientOut],
    summary="List catalog ingredients",
)
def list_catalog_ingredients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[IngredientOut]:
    return [IngredientOut.model_validate(i) for i in list_ingredients(db)]
