"""Product persistence for the active routine."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Product, User


def list_products(db: Session, user_id: str) -> list[Product]:
    return list(
        db.scalars(
            select(Product)
            .where(Product.user_id == user_id)
            .order_by(Product.is_active.desc(), Product.created_at.desc())
        )
    )


def active_ingredients(db: Session, user_id: str) -> list[str]:
    ingredients: list[str] = []
    for product in list_products(db, user_id):
        if not product.is_active:
            continue
        for ingredient in product.key_ingredients or []:
            if ingredient not in ingredients:
                ingredients.append(ingredient)
    return ingredients


def find_by_name(db: Session, user_id: str, name: str) -> Product | None:
    return db.scalar(
        select(Product).where(
            Product.user_id == user_id,
            func.lower(Product.name) == name.strip().lower(),
        )
    )


def upsert_product(
    db: Session,
    user: User,
    *,
    name: str,
    brand: str = "",
    key_ingredients: list[str] | None = None,
    inci_text: str | None = None,
    is_active: bool = True,
    source: str = "manual",
) -> Product:
    product = find_by_name(db, user.id, name)
    if product is None:
        product = Product(user_id=user.id, name=name.strip(), source=source)
        db.add(product)

    product.brand = brand.strip()
    product.key_ingredients = list(key_ingredients or [])
    if inci_text:
        product.inci_text = inci_text
    product.is_active = is_active
    product.source = source
    db.flush()
    return product
