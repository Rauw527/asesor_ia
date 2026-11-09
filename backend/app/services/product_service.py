"""Catalog product service."""

from __future__ import annotations

from app.repositories import catalog_product_repository


def list_products(db):
    return catalog_product_repository.list_products(db)


def get_product(db, product_id: str):
    return catalog_product_repository.get_product(db, product_id)


def seed_products(db):
    catalog_product_repository.seed_products(db)
    db.commit()
