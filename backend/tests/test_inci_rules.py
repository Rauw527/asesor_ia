"""Unit tests for the deterministic INCI rule engine."""

from app.services import inci_rules


def test_alias_normalization_matches_spanish_and_inci_names() -> None:
    canonical, unknown = inci_rules.normalize_ingredients(
        ["Ácido Glicólico", "NIACINAMIDE", "Agua"]
    )
    assert canonical[:2] == ["glycolic_acid", "niacinamide"]
    assert unknown == ["agua"]


def test_conflict_detected_inside_scanned_product() -> None:
    verdict = inci_rules.evaluate(["Retinol", "Glycolic Acid"], skin_type="Mixta")
    assert verdict.has_conflict is True
    assert len(verdict.findings) == 1
    assert verdict.findings[0].severity == "alta"
    assert "Retinol" in verdict.warning
    assert "glicólico" in verdict.warning.lower()


def test_conflict_detected_against_active_routine() -> None:
    verdict = inci_rules.evaluate(
        ["Salicylic Acid"], routine_ingredients=["Retinol 0.5%"], skin_type="Grasa"
    )
    assert verdict.has_conflict is True
    assert verdict.findings[0].severity == "alta"


def test_conflict_fully_inside_routine_is_not_blamed_on_scanned_product() -> None:
    verdict = inci_rules.evaluate(
        ["Niacinamide"],
        routine_ingredients=["Retinol", "Glycolic Acid"],
        skin_type="Mixta",
    )
    assert verdict.has_conflict is False
    assert verdict.findings == []


def test_safe_product_reports_no_conflict() -> None:
    verdict = inci_rules.evaluate(
        ["Aqua", "Glycerin", "Niacinamide", "Panthenol"], skin_type="Seca"
    )
    assert verdict.has_conflict is False
    assert verdict.unknown == ["aqua"]
    assert "Niacinamida" in verdict.recognized


def test_sensitive_skin_flags_fragrance() -> None:
    verdict = inci_rules.evaluate(["Parfum", "Glycerin"], skin_type="Sensible")
    assert verdict.has_conflict is True
    assert verdict.sensitive_triggers == ["Fragancia / perfume"]


def test_medium_severity_sorted_after_high() -> None:
    verdict = inci_rules.evaluate(["Retinol", "Glycolic Acid", "Ascorbic Acid"], skin_type="Mixta")
    severities = [finding.severity for finding in verdict.findings]
    assert severities == sorted(severities, key=lambda value: 0 if value == "alta" else 1)


def test_ingredient_dictionary_is_consistent() -> None:
    matrix = inci_rules.conflict_matrix_for_seed()
    for canonical, conflicts in matrix.items():
        assert canonical in inci_rules.INGREDIENTS
        for other in conflicts:
            assert other in inci_rules.INGREDIENTS
            assert canonical in matrix[other]
