"""Catalog product persistence helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalog_product import CatalogProduct


def list_products(db: Session) -> list[CatalogProduct]:
    return list(db.execute(select(CatalogProduct).order_by(CatalogProduct.name)).scalars())


def get_product(db: Session, product_id: str) -> CatalogProduct | None:
    return db.get(CatalogProduct, product_id)


def seed_products(db: Session) -> None:
    """Inserts clearly identified demo/fictitious products for the MVP."""
    existing = db.execute(select(CatalogProduct)).scalars().first()
    if existing:
        return

    seed = [
        {
            "name": "Gentle Cleansing Gel (Demo)",
            "brand": "Facial y Moda",
            "category": "Cleanser",
            "description": "Demo cleanser for morning and night use.",
            "inci_list": ["Aqua", "Glycerin"],
            "active_ingredients": ["Glycerin"],
            "function": "Gentle cleansing",
            "concentration_declared": None,
            "warnings": "Avoid contact with eyes.",
            "price_guide": "$12",
            "image_url": None,
            "availability": "Demo",
            "is_demo_data": True,
        },
        {
            "name": "Light Hydrating Cream (Demo)",
            "brand": "Facial y Moda",
            "category": "Moisturizer",
            "description": "Demo lightweight moisturizer.",
            "inci_list": ["Aqua", "Glycerin", "Niacinamide"],
            "active_ingredients": ["Glycerin", "Niacinamide"],
            "function": "Hydration",
            "concentration_declared": None,
            "warnings": "Patch test before first use.",
            "price_guide": "$18",
            "image_url": None,
            "availability": "Demo",
            "is_demo_data": True,
        },
        {
            "name": "Mineral Sunscreen SPF 30 (Demo)",
            "brand": "Facial y Moda",
            "category": "Sunscreen",
            "description": "Demo mineral sunscreen for daytime.",
            "inci_list": ["Aqua", "Zinc Oxide", "Glycerin"],
            "active_ingredients": ["Zinc Oxide"],
            "function": "UV protection",
            "concentration_declared": None,
            "warnings": "Reapply every 2 hours when exposed to sun.",
            "price_guide": "$22",
            "image_url": None,
            "availability": "Demo",
            "is_demo_data": True,
        },
        {
            "name": "BHA Exfoliant 2% (Demo)",
            "brand": "Facial y Moda",
            "category": "Treatment",
            "description": "Demo salicylic acid exfoliant for night use.",
            "inci_list": ["Aqua", "Salicylic Acid"],
            "active_ingredients": ["Salicylic Acid"],
            "function": "Pore cleansing",
            "concentration_declared": None,
            "warnings": "Use only at night. Do not combine with retinol.",
            "price_guide": "$20",
            "image_url": None,
            "availability": "Demo",
            "is_demo_data": True,
        },
        {
            "name": "Vitamin C Serum (Demo)",
            "brand": "Facial y Moda",
            "category": "Treatment",
            "description": "Demo antioxidant serum for morning use.",
            "inci_list": ["Aqua", "Ascorbic Acid", "Glycerin"],
            "active_ingredients": ["Ascorbic Acid"],
            "function": "Antioxidant",
            "concentration_declared": None,
            "warnings": "Use in the morning; always pair with sunscreen.",
            "price_guide": "$25",
            "image_url": None,
            "availability": "Demo",
            "is_demo_data": True,
        },
    ]

    for item in seed:
        db.add(CatalogProduct(**item))
    db.flush()
