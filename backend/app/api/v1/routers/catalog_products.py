"""Catalog product endpoints (reference data)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.catalog_product import CatalogProductOut
from app.services.product_service import get_product, list_products

router = APIRouter(prefix="/catalog", tags=["catalog-products"])


@router.get(
    "/products",
    response_model=list[CatalogProductOut],
    summary="List catalog products",
)
def list_catalog_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CatalogProductOut]:
    return [CatalogProductOut.model_validate(p) for p in list_products(db)]


@router.get(
    "/products/{product_id}",
    response_model=CatalogProductOut,
    summary="Get a catalog product detail",
)
def get_catalog_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CatalogProductOut:
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return CatalogProductOut.model_validate(product)
