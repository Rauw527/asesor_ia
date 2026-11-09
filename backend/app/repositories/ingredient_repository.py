"""Ingredient catalog persistence helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient


def list_ingredients(db: Session) -> list[Ingredient]:
    return list(db.execute(select(Ingredient).order_by(Ingredient.inci_name)).scalars())


def get_ingredient(db: Session, ingredient_id: str) -> Ingredient | None:
    return db.get(Ingredient, ingredient_id)


def seed_ingredients(db: Session) -> None:
    """Inserts a small verified seed of common cosmetic ingredients."""
    existing = db.execute(select(Ingredient)).scalars().first()
    if existing:
        return

    seed = [
        {
            "inci_name": "Aqua",
            "common_name": "Water",
            "function": "Solvent",
            "description": "Base solvent used in most cosmetic formulations.",
            "precautions": None,
            "evidence_level": "Established",
            "sources": "INCI dictionary",
        },
        {
            "inci_name": "Glycerin",
            "common_name": "Glycerol",
            "function": "Humectant",
            "description": "Attracts water to the skin, helping maintain hydration.",
            "precautions": "Generally well tolerated.",
            "evidence_level": "Established",
            "sources": "INCI dictionary",
        },
        {
            "inci_name": "Niacinamide",
            "common_name": "Vitamin B3",
            "function": "Skin conditioning",
            "description": "Helps improve skin barrier and even out skin tone.",
            "precautions": "Use with caution in very high concentrations.",
            "evidence_level": "Established",
            "sources": "Clinical literature",
        },
        {
            "inci_name": "Salicylic Acid",
            "common_name": "BHA",
            "function": "Exfoliant",
            "description": "Beta-hydroxy acid that helps unclog pores.",
            "precautions": "Can cause dryness or irritation; avoid combining with retinol.",
            "evidence_level": "Established",
            "sources": "Clinical literature",
        },
        {
            "inci_name": "Retinol",
            "common_name": "Vitamin A",
            "function": "Anti-aging",
            "description": "Supports skin renewal and reduces fine lines.",
            "precautions": "Photosensitizing; use at night and with sunscreen by day.",
            "evidence_level": "Established",
            "sources": "Clinical literature",
        },
        {
            "inci_name": "Ascorbic Acid",
            "common_name": "Vitamin C",
            "function": "Antioxidant",
            "description": "Helps protect against oxidative stress and brighten skin.",
            "precautions": "Can be unstable; store away from light and air.",
            "evidence_level": "Established",
            "sources": "Clinical literature",
        },
        {
            "inci_name": "Zinc Oxide",
            "common_name": None,
            "function": "UV filter",
            "description": "Mineral sunscreen agent that reflects UV radiation.",
            "precautions": "May leave a white cast on darker skin tones.",
            "evidence_level": "Established",
            "sources": "Regulatory monographs",
        },
    ]

    for item in seed:
        db.add(Ingredient(**item))
    db.flush()
