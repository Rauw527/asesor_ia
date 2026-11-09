"""User profile endpoint and the routine product registry.

The product registry is what makes the INCI audit meaningful: the scanned label
is cross-checked against the actives the user actually uses.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.repositories import product_repository, user_repository
from app.schemas.user import UserOut

router = APIRouter(tags=["users"])


class ProductCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=160)
    brand: str = Field(default="", max_length=120)
    key_ingredients: list[str] = Field(default_factory=list, max_length=60)
    is_active: bool = True
    user_id: str | None = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    brand: str
    key_ingredients: list[str]
    is_active: bool
    source: str


@router.get("/users/me", response_model=UserOut, summary="Perfil del usuario demo")
def get_me(user_id: str | None = None, db: Session = Depends(get_db)) -> UserOut:
    user = user_repository.resolve_user(db, user_id, get_settings())
    db.commit()  # persists the demo user on first boot
    return UserOut.model_validate(user)


@router.get("/products", response_model=list[ProductOut], summary="Productos de la rutina")
def list_products(user_id: str | None = None, db: Session = Depends(get_db)) -> list[ProductOut]:
    user = user_repository.resolve_user(db, user_id, get_settings())
    return [
        ProductOut.model_validate(item) for item in product_repository.list_products(db, user.id)
    ]


@router.post(
    "/products",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    summary="Añade un producto a la rutina activa",
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> ProductOut:
    user = user_repository.resolve_user(db, payload.user_id, get_settings())
    product = product_repository.upsert_product(
        db,
        user,
        name=payload.name,
        brand=payload.brand,
        key_ingredients=payload.key_ingredients,
        is_active=payload.is_active,
        source="manual",
    )
    db.commit()
    return ProductOut.model_validate(product)
