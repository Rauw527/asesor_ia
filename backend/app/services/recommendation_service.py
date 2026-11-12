"""Conservative, transparent demo routines based on declared preferences."""

from app.repositories import questionnaire_repository, routine_repository


def generate_routine(db, user_id: str, routine_type: str, assessment):
    questionnaire = questionnaire_repository.get_latest_questionnaire(db, user_id)
    answers = (
        {a.question_key: a.answer_value for a in questionnaire.answers} if questionnaire else {}
    )
    sensitive = assessment.sensitivity in {"alta", "media"} or assessment.sensitivity is None
    skin_type = assessment.perceived_skin_type or "no determinado"
    steps = [
        {
            "order": 1,
            "step": "cleansing",
            "title": "Limpieza suave",
            "explanation": f"Punto de partida para tu perfil declarado ({skin_type}). Usa las instrucciones de tu producto; no es un diagnóstico.",
            "suggested_products": [],
        }
    ]
    steps.append(
        {
            "order": 2,
            "step": "moisturizing",
            "title": "Hidratación",
            "explanation": (
                "Has indicado sensibilidad o no estás seguro: esta demo no añade tratamientos activos. "
                if sensitive
                else ""
            )
            + "Organiza este paso con un producto que ya toleres. No se ha verificado la idoneidad de productos concretos.",
            "suggested_products": [],
        }
    )
    if routine_type == "morning":
        steps.append(
            {
                "order": 3,
                "step": "sunscreen",
                "title": "Protección solar",
                "explanation": "Consulta y sigue las indicaciones del envase. Esta demo organiza pasos y no prescribe tratamientos.",
                "suggested_products": [],
            }
        )
    for step in steps:
        step["preference_note"] = (
            "Tiempo preferido: "
            + answers.get("time", "sin indicar")
            + ". Presupuesto: "
            + answers.get("budget", "sin indicar")
            + "."
        )
    routine = routine_repository.save_routine(
        db,
        user_id=user_id,
        routine_type=routine_type,
        steps=steps,
        generated_from="questionnaire_demo_rules_v1",
    )
    db.commit()
    return routine


def list_user_routines(db, user_id):
    return routine_repository.list_routines(db, user_id)


def get_routine(db, routine_id, user_id):
    return routine_repository.get_routine(db, routine_id, user_id)
