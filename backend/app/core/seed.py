"""Idempotent reference-data seeding (ingredient dictionary + demo user)."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import INCIIngredient
from app.repositories.catalog_product_repository import seed_products
from app.repositories.ingredient_repository import seed_ingredients
from app.repositories.user_repository import get_or_create_demo_user
from app.services.inci_rules import INGREDIENTS, conflict_matrix_for_seed

logger = logging.getLogger(__name__)


def seed_reference_data(session: Session, config: Settings) -> None:
    matrix = conflict_matrix_for_seed()
    existing = {row.inci_name: row for row in session.scalars(select(INCIIngredient)).all()}

    created = 0
    for canonical, info in INGREDIENTS.items():
        row = existing.get(canonical)
        if row is None:
            row = INCIIngredient(inci_name=canonical)
            session.add(row)
            created += 1

        row.display_name = info.display_name
        row.category = info.category
        row.aliases = list(info.aliases)
        row.conflicts_with = matrix[canonical]
        row.risk_notes = info.notes

    get_or_create_demo_user(session, config)

    # New Facial y Moda catalogs (clearly marked demo data)
    seed_ingredients(session)
    seed_products(session)

    session.flush()

    if created:
        logger.info("Seeded %d INCI reference ingredients", created)
    logger.info("Seeded Facial y Moda ingredient + product catalogs")
