"""SkinProfileService: combines questionnaire + visual analysis + history."""

from __future__ import annotations

from app.repositories import (
    ingredient_repository,
    questionnaire_repository,
    skin_assessment_repository,
    skin_analysis_repository,
)


def build_assessment(db, user_id: str):
    """Combine available data into an orientative skin profile."""
    questionnaire = questionnaire_repository.get_latest_questionnaire(db, user_id)
    latest_analysis = None
    analyses = skin_analysis_repository.list_analyses(db, user_id)
    if analyses:
        latest_analysis = analyses[0]

    # Determine data source
    has_questionnaire = questionnaire is not None and questionnaire.completed
    has_visual = latest_analysis is not None

    if has_questionnaire and has_visual:
        data_source = "mixed"
    elif has_visual:
        data_source = "visual"
    elif has_questionnaire:
        data_source = "questionnaire"
    else:
        data_source = "none"

    # Derive perceived skin type from questionnaire answers if available
    perceived_skin_type = None
    sensitivity = None
    main_concerns: list[str] = []

    if has_questionnaire:
        answers = {a.question_key: a.answer_value for a in questionnaire.answers}
        perceived_skin_type = answers.get("skin_feeling")
        if answers.get("irritates_easily") == "Sí":
            sensitivity = "alta"
        elif answers.get("irritates_easily") == "Algunas veces":
            sensitivity = "media"
        else:
            sensitivity = "baja"

        concern = answers.get("main_concern")
        if concern:
            main_concerns.append(concern)

    # If visual analysis exists but is demo, observations are null (no real data)
    visual_status = "demo"
    if latest_analysis and latest_analysis.analysis_status == "real":
        visual_status = "real"

    assessment = skin_assessment_repository.save_assessment(
        db,
        user_id=user_id,
        perceived_skin_type=perceived_skin_type,
        sensitivity=sensitivity,
        main_concerns=main_concerns,
        questionnaire_completed=bool(has_questionnaire),
        visual_analysis_status=visual_status,
        data_source=data_source,
    )
    db.commit()
    return assessment


def get_user_assessment(db, user_id: str):
    return skin_assessment_repository.get_assessment(db, user_id)
