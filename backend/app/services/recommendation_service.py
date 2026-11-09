"""SkinRecommendationEngine: generates morning/night routines."""

from __future__ import annotations

from app.repositories import catalog_product_repository, ingredient_repository


def _find_products_by_function(db, function_keywords: list[str], limit: int = 2):
    products = catalog_product_repository.list_products(db)
    matched = []
    for p in products:
        text = " ".join(
            [
                p.name or "",
                p.function or "",
                " ".join(p.active_ingredients or []),
                " ".join(p.inci_list or []),
            ]
        ).lower()
        if any(kw.lower() in text for kw in function_keywords):
            matched.append(p)
    return matched[:limit]


def generate_routine(db, user_id: str, routine_type: str, assessment):
    """Build a morning or night routine based on the skin assessment."""
    from app.repositories import routine_repository

    steps: list[dict] = []
    generated_from = "questionnaire"

    if routine_type == "morning":
        steps = [
            {
                "order": 1,
                "step": "cleansing",
                "title": "Limpieza",
                "explanation": "Elimina impurezas y exceso de grasa acumulado durante la noche.",
            },
            {
                "order": 2,
                "step": "moisturizing",
                "title": "Hidratación",
                "explanation": "Restaura la barrera cutánea y mantiene la piel hidratada durante el día.",
            },
            {
                "order": 3,
                "step": "sunscreen",
                "title": "Protección solar",
                "explanation": "Protege contra radiación UV y previene manchas y envejecimiento prematuro.",
            },
        ]
        generated_from = "questionnaire"
    else:  # night
        steps = [
            {
                "order": 1,
                "step": "cleansing",
                "title": "Limpieza",
                "explanation": "Elimina residuos de protector solar, contaminación y sebo del día.",
            },
        ]
        # Treatment when appropriate (based on concerns)
        concerns = assessment.main_concerns if assessment else []
        if any(c.lower() in ("acné", "acne", "manchas", "brillo excesivo") for c in concerns):
            steps.append(
                {
                    "order": 2,
                    "step": "treatment",
                    "title": "Tratamiento nocturno",
                    "explanation": "Activos específicos para tratar preocupaciones declaradas (acné, manchas, brillo).",
                }
            )
        steps.append(
            {
                "order": len(steps) + 1,
                "step": "moisturizing",
                "title": "Hidratación",
                "explanation": "Repara y nutre la piel mientras duermes.",
            }
        )

    # Attach suggested products to steps
    for step in steps:
        if step["step"] == "cleansing":
            products = _find_products_by_function(db, ["cleanser", "limpieza"], 1)
        elif step["step"] == "moisturizing":
            products = _find_products_by_function(db, ["moisturizer", "hidratación", "hidratacion"], 1)
        elif step["step"] == "sunscreen":
            products = _find_products_by_function(db, ["sunscreen", "protección solar", "proteccion solar"], 1)
        elif step["step"] == "treatment":
            products = _find_products_by_function(db, ["treatment", "tratamiento", "exfoliant"], 1)
        else:
            products = []
        step["suggested_products"] = [
            {
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "function": p.function,
                "warnings": p.warnings,
                "is_demo_data": p.is_demo_data,
            }
            for p in products
        ]

    routine = routine_repository.save_routine(
        db,
        user_id=user_id,
        routine_type=routine_type,
        steps=steps,
        generated_from=generated_from,
    )
    db.commit()
    return routine


def list_user_routines(db, user_id: str):
    from app.repositories import routine_repository

    return routine_repository.list_routines(db, user_id)


def get_routine(db, routine_id: str, user_id: str):
    from app.repositories import routine_repository

    return routine_repository.get_routine(db, routine_id, user_id)
