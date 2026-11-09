"""Ingredient catalog service."""

from __future__ import annotations

from app.repositories import ingredient_repository


def list_ingredients(db):
    return ingredient_repository.list_ingredients(db)


def get_ingredient(db, ingredient_id: str):
    return ingredient_repository.get_ingredient(db, ingredient_id)


def seed_ingredients(db):
    ingredient_repository.seed_ingredients(db)
    db.commit()
