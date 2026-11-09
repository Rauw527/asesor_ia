"""Deterministic INCI conflict engine.

Why a rule engine on top of the LLM:

* compatibility between common actives is well-known chemistry, not something we
  should pay a model to guess on every scan;
* the verdict stays stable, auditable and instant for the ~40 actives that cover
  most of the market;
* the LLM is only asked to read the label (OCR), which is where it is genuinely
  better than a parser.

Unknown ingredients are still returned to the caller; they are reported as
``unknown`` instead of being silently treated as safe.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Literal

Severity = Literal["alta", "media"]


@dataclass(frozen=True)
class IngredientInfo:
    canonical: str
    display_name: str
    category: str
    aliases: tuple[str, ...]
    notes: str = ""


@dataclass(frozen=True)
class ConflictRule:
    a: str
    b: str
    severity: Severity
    message: str
    recommendation: str


@dataclass(frozen=True)
class ConflictFinding:
    canonicals: tuple[str, str]
    ingredients: tuple[str, str]
    severity: Severity
    message: str
    recommendation: str


@dataclass
class InciVerdict:
    has_conflict: bool
    findings: list[ConflictFinding] = field(default_factory=list)
    recognized: list[str] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)
    sensitive_triggers: list[str] = field(default_factory=list)

    @property
    def warning(self) -> str | None:
        parts: list[str] = []
        for finding in self.findings:
            parts.append(f"{finding.message} {finding.recommendation}".strip())
        if self.sensitive_triggers and not parts:
            parts.append(
                "Tu perfil es de piel sensible y este producto contiene "
                + ", ".join(self.sensitive_triggers)
                + ". Vigila la irritación y espacia su uso."
            )
        return " ".join(parts) if parts else None


def normalize(text: str) -> str:
    """Lowercase, strip accents/punctuation and collapse whitespace."""
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(char for char in decomposed if not unicodedata.combining(char))
    cleaned = re.sub(r"[^a-z0-9 ]+", " ", ascii_text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _info(canonical: str) -> IngredientInfo:
    return INGREDIENTS[canonical]


INGREDIENTS: dict[str, IngredientInfo] = {
    info.canonical: info
    for info in [
        IngredientInfo(
            "retinol",
            "Retinol",
            "retinoide",
            ("retinol", "retinal", "retinaldehyde", "retinaldehido", "retinyl retinoate"),
            "Activo anti-edad. Requiere rutina nocturna y protector solar diario.",
        ),
        IngredientInfo(
            "retinyl_palmitate",
            "Retinil palmitato",
            "retinoide",
            ("retinyl palmitate", "retinil palmitato"),
            "Derivado suave del retinol.",
        ),
        IngredientInfo(
            "bakuchiol",
            "Bakuchiol",
            "retinoide_vegetal",
            ("bakuchiol",),
            "Alternativa vegetal al retinol, normalmente bien tolerada.",
        ),
        IngredientInfo(
            "glycolic_acid",
            "Ácido glicólico",
            "aha",
            ("glycolic acid", "acido glicolico", "glycolic"),
            "AHA exfoliante. Puede aumentar la fotosensibilidad.",
        ),
        IngredientInfo(
            "lactic_acid",
            "Ácido láctico",
            "aha",
            ("lactic acid", "acido lactico"),
            "AHA suave, también humectante.",
        ),
        IngredientInfo(
            "mandelic_acid",
            "Ácido mandélico",
            "aha",
            ("mandelic acid", "acido mandelico"),
            "AHA de molécula grande, buena tolerancia.",
        ),
        IngredientInfo(
            "salicylic_acid",
            "Ácido salicílico",
            "bha",
            ("salicylic acid", "acido salicilico", "bha"),
            "BHA liposoluble, útil en poros y comedones.",
        ),
        IngredientInfo(
            "gluconolactone",
            "Gluconolactona",
            "pha",
            ("gluconolactone", "gluconolactona", "pha"),
            "PHA exfoliante muy suave.",
        ),
        IngredientInfo(
            "ascorbic_acid",
            "Vitamina C (ácido ascórbico)",
            "antioxidante",
            ("ascorbic acid", "acido ascorbico", "vitamin c", "vitamina c"),
            "Antioxidante; inestable frente a luz y pH alto.",
        ),
        IngredientInfo(
            "ascorbyl_glucoside",
            "Ascorbil glucósido",
            "antioxidante",
            ("ascorbyl glucoside", "ascorbil glucosido", "sodium ascorbyl phosphate"),
            "Derivado estable de vitamina C.",
        ),
        IngredientInfo(
            "niacinamide",
            "Niacinamida",
            "vitamina_b3",
            ("niacinamide", "niacinamida", "nicotinamide", "nicotinamida"),
            "Regula sebo y refuerza la barrera.",
        ),
        IngredientInfo(
            "hyaluronic_acid",
            "Ácido hialurónico",
            "humectante",
            ("hyaluronic acid", "acido hialuronico", "sodium hyaluronate", "hyaluronate"),
            "Humectante de alto peso molecular.",
        ),
        IngredientInfo(
            "glycerin",
            "Glicerina",
            "humectante",
            ("glycerin", "glycerol", "glicerina"),
            "Humectante universal, muy bien tolerado.",
        ),
        IngredientInfo(
            "panthenol",
            "Pantenol",
            "calmante",
            ("panthenol", "provitamin b5", "dexpanthenol"),
            "Calmante y reparador de barrera.",
        ),
        IngredientInfo(
            "centella",
            "Centella asiática",
            "calmante",
            ("centella asiatica", "madecassoside", "asiaticoside", "cica"),
            "Calmante vegetal.",
        ),
        IngredientInfo(
            "allantoin",
            "Alantoína",
            "calmante",
            ("allantoin", "alantoina"),
            "Calmante y queratolítico suave.",
        ),
        IngredientInfo(
            "ceramides",
            "Ceramidas",
            "barrera",
            ("ceramide", "ceramides", "ceramida", "ceramidas"),
            "Lípidos de barrera cutánea.",
        ),
        IngredientInfo(
            "squalane",
            "Escualano",
            "emoliente",
            ("squalane", "escualano", "squalene"),
            "Emoliente ligero no comedogénico.",
        ),
        IngredientInfo(
            "azelaic_acid",
            "Ácido azelaico",
            "activo",
            ("azelaic acid", "acido azelaico"),
            "Activo para rojeces y marcas; suele tolerarse bien.",
        ),
        IngredientInfo(
            "hydroquinone",
            "Hidroquinona",
            "despigmentante",
            ("hydroquinone", "hidroquinona"),
            "Despigmentante potente; requiere control profesional.",
        ),
        IngredientInfo(
            "arbutin",
            "Arbutina",
            "despigmentante",
            ("arbutin", "arbutina", "alpha arbutin"),
            "Despigmentante suave.",
        ),
        IngredientInfo(
            "tranexamic_acid",
            "Ácido tranexámico",
            "despigmentante",
            ("tranexamic acid", "acido tranexamico"),
            "Ayuda con manchas y rojeces.",
        ),
        IngredientInfo(
            "kojic_acid",
            "Ácido kójico",
            "despigmentante",
            ("kojic acid", "acido kojico"),
            "Despigmentante; puede irritar pieles sensibles.",
        ),
        IngredientInfo(
            "benzoyl_peroxide",
            "Peróxido de benzoilo",
            "antimicrobiano",
            ("benzoyl peroxide", "peroxido de benzoilo", "bpo"),
            "Antiacné potente y secante.",
        ),
        IngredientInfo(
            "zinc_pca",
            "Zinc PCA",
            "seborregulador",
            ("zinc pca", "zinc gluconate"),
            "Regula sebo y calma.",
        ),
        IngredientInfo(
            "sulfur",
            "Azufre",
            "antimicrobiano",
            ("sulfur", "azufre"),
            "Antiacné clásico, puede resecar.",
        ),
        IngredientInfo(
            "tea_tree_oil",
            "Aceite de árbol de té",
            "antimicrobiano",
            ("tea tree oil", "melaleuca alternifolia", "arbol de te"),
            "Antiséptico; irritante en concentración alta.",
        ),
        IngredientInfo(
            "fragrance",
            "Fragancia / perfume",
            "irritante",
            ("fragrance", "parfum", "perfume", "aroma", "fragancia"),
            "Principal causa de sensibilización cosmética.",
        ),
        IngredientInfo(
            "alcohol_denat",
            "Alcohol desnaturalizado",
            "irritante",
            ("alcohol denat", "denatured alcohol", "sd alcohol", "ethanol", "alcohol"),
            "Puede resecar la barrera en fórmulas con alta concentración.",
        ),
        IngredientInfo(
            "essential_oils",
            "Aceites esenciales",
            "irritante",
            ("limonene", "linalool", "citronellol", "geraniol", "eugenol", "citral"),
            "Alérgenos frecuentes declarados en el etiquetado.",
        ),
        IngredientInfo(
            "sls",
            "Sodium Lauryl Sulfate",
            "tensioactivo",
            ("sodium lauryl sulfate", "sls", "lauril sulfato de sodio"),
            "Tensioactivo agresivo para piel sensible.",
        ),
        IngredientInfo(
            "zinc_oxide",
            "Óxido de zinc",
            "filtro_solar",
            ("zinc oxide", "oxido de zinc"),
            "Filtro físico con cobertura y control de sebo.",
        ),
        IngredientInfo(
            "titanium_dioxide",
            "Dióxido de titanio",
            "filtro_solar",
            ("titanium dioxide", "dioxido de titanio"),
            "Filtro físico.",
        ),
        IngredientInfo(
            "avobenzone",
            "Avobenzona",
            "filtro_solar",
            ("avobenzone", "butyl methoxydibenzoylmethane"),
            "Filtro químico UVA.",
        ),
        IngredientInfo(
            "peptides",
            "Péptidos",
            "activo",
            ("peptide", "peptides", "palmitoyl tripeptide", "matrixyl", "argireline"),
            "Señales de reparación, buena tolerancia.",
        ),
        IngredientInfo(
            "caffeine",
            "Cafeína",
            "activo",
            ("caffeine", "cafeina"),
            "Descongestionante en contorno de ojos.",
        ),
        IngredientInfo(
            "vitamin_e",
            "Vitamina E (tocoferol)",
            "antioxidante",
            ("tocopherol", "tocopheryl acetate", "vitamin e", "vitamina e"),
            "Antioxidante y emoliente.",
        ),
        IngredientInfo(
            "urea",
            "Urea",
            "humectante",
            ("urea",),
            "Humectante y queratolítico según concentración.",
        ),
        IngredientInfo(
            "witch_hazel",
            "Hamamelis",
            "astringente",
            ("hamamelis virginiana", "witch hazel", "hamamelis"),
            "Astringente; puede resecar por su contenido alcohólico.",
        ),
    ]
}

CONFLICT_RULES: tuple[ConflictRule, ...] = (
    ConflictRule(
        "retinol",
        "glycolic_acid",
        "alta",
        "Retinol y ácido glicólico juntos en la misma rutina aumentan irritación y descamación.",
        "Alterna noches (por ejemplo, retinol lunes/jueves y AHA martes/viernes).",
    ),
    ConflictRule(
        "retinol",
        "salicylic_acid",
        "alta",
        "Retinol y ácido salicílico combinados pueden sobre-exfoliar y dañar la barrera.",
        "Usa el BHA por la mañana y el retinol por la noche, o alterna días.",
    ),
    ConflictRule(
        "retinol",
        "benzoyl_peroxide",
        "alta",
        "El peróxido de benzoilo inactiva el retinol y ambos irritan en conjunto.",
        "Separa su uso por franjas horarias o elige uno solo hasta que la piel se adapte.",
    ),
    ConflictRule(
        "retinol",
        "ascorbic_acid",
        "media",
        "Retinol y vitamina C directa pueden irritar si se aplican sin intervalo.",
        "Vitamina C por la mañana y retinol por la noche.",
    ),
    ConflictRule(
        "retinol",
        "hydroquinone",
        "alta",
        "Retinol e hidroquinona juntos elevan el riesgo de irritación marcada.",
        "Consulta con un profesional y espacia los activos.",
    ),
    ConflictRule(
        "glycolic_acid",
        "salicylic_acid",
        "media",
        "AHA + BHA en el mismo paso duplican la exfoliación.",
        "Alterna formulaciones o reduce la frecuencia a 2 veces por semana.",
    ),
    ConflictRule(
        "glycolic_acid",
        "benzoyl_peroxide",
        "media",
        "AHA y peróxido de benzoilo resecan e irritan la piel en conjunto.",
        "Separa su aplicación por horarios.",
    ),
    ConflictRule(
        "ascorbic_acid",
        "benzoyl_peroxide",
        "alta",
        "El peróxido de benzoilo oxida la vitamina C y anula su efecto.",
        "Vitamina C por la mañana, peróxido de benzoilo por la noche.",
    ),
    ConflictRule(
        "niacinamide",
        "ascorbic_acid",
        "media",
        "Niacinamida y vitamina C directa pueden provocar rubor transitorio en pieles sensibles.",
        "Aplica una por la mañana y otra por la noche si notas irritación.",
    ),
    ConflictRule(
        "salicylic_acid",
        "benzoyl_peroxide",
        "media",
        "BHA y peróxido de benzoilo son muy secantes juntos.",
        "Alterna días y refuerza la hidratación.",
    ),
    ConflictRule(
        "hydroquinone",
        "benzoyl_peroxide",
        "alta",
        "La combinación puede producir pigmentación irregular.",
        "No los combines sin supervisión profesional.",
    ),
    ConflictRule(
        "azelaic_acid",
        "retinol",
        "media",
        "Ácido azelaico y retinol pueden irritar al inicio del tratamiento.",
        "Introduce uno a la vez con dos semanas de diferencia.",
    ),
    ConflictRule(
        "kojic_acid",
        "glycolic_acid",
        "media",
        "Ácido kójico con AHA aumenta la sensibilidad y el riesgo de irritación.",
        "Alterna días y usa protector solar a diario.",
    ),
)

SENSITIVE_TRIGGERS: frozenset[str] = frozenset(
    {"fragrance", "alcohol_denat", "essential_oils", "sls", "tea_tree_oil"}
)

# Pre-computed lookup: token -> canonical, longest alias first to reduce
# accidental substring matches.
_ALIAS_INDEX: list[tuple[str, str]] = sorted(
    (
        (normalize(alias), canonical)
        for canonical, info in INGREDIENTS.items()
        for alias in (info.display_name, *info.aliases)
    ),
    key=lambda pair: len(pair[0]),
    reverse=True,
)


def _tokenize(raw_ingredients: list[str]) -> list[str]:
    tokens: list[str] = []
    for raw in raw_ingredients:
        for chunk in re.split(r"[,;\n]", raw):
            normalized = normalize(chunk)
            if normalized:
                tokens.append(normalized)
    return tokens


def match_ingredient(token: str) -> str | None:
    normalized = normalize(token)
    if not normalized:
        return None
    for alias, canonical in _ALIAS_INDEX:
        if normalized == alias or re.search(rf"(^|\s){re.escape(alias)}(\s|$)", normalized):
            return canonical
    return None


def normalize_ingredients(raw_ingredients: list[str]) -> tuple[list[str], list[str]]:
    """Return (recognized canonicals, unknown tokens) preserving order."""
    recognized: list[str] = []
    unknown: list[str] = []
    for token in _tokenize(raw_ingredients):
        canonical = match_ingredient(token)
        if canonical is None:
            unknown.append(token)
        elif canonical not in recognized:
            recognized.append(canonical)
    return recognized, unknown


def _find_conflicts(canonicals: list[str]) -> list[ConflictFinding]:
    present = set(canonicals)
    findings: list[ConflictFinding] = []
    for rule in CONFLICT_RULES:
        if {rule.a, rule.b} <= present:
            findings.append(
                ConflictFinding(
                    canonicals=(rule.a, rule.b),
                    ingredients=(_info(rule.a).display_name, _info(rule.b).display_name),
                    severity=rule.severity,
                    message=rule.message,
                    recommendation=rule.recommendation,
                )
            )
    findings.sort(key=lambda finding: 0 if finding.severity == "alta" else 1)
    return findings


def evaluate(
    scanned_ingredients: list[str],
    routine_ingredients: list[str] | None = None,
    skin_type: str | None = None,
) -> InciVerdict:
    """Cross-check a scanned label against the user's active routine."""
    routine_ingredients = routine_ingredients or []
    scanned_canonicals, unknown = normalize_ingredients(scanned_ingredients)
    routine_canonicals, _ = normalize_ingredients(routine_ingredients)

    scanned_set = set(scanned_canonicals)
    # Only report a pair when the scanned product takes part in it. A conflict
    # that already exists inside the user's routine is not this product's fault.
    findings = [
        finding
        for finding in _find_conflicts(sorted(scanned_set | set(routine_canonicals)))
        if scanned_set.intersection(finding.canonicals)
    ]

    triggers: list[str] = []
    if skin_type and normalize(skin_type) in {"sensible", "sensitive"}:
        triggers = [
            _info(canonical).display_name
            for canonical in scanned_canonicals
            if canonical in SENSITIVE_TRIGGERS
        ]

    return InciVerdict(
        has_conflict=bool(findings) or bool(triggers),
        findings=findings,
        recognized=[_info(canonical).display_name for canonical in scanned_canonicals],
        unknown=unknown,
        sensitive_triggers=triggers,
    )


def conflict_matrix_for_seed() -> dict[str, list[str]]:
    """canonical -> conflicting canonicals (used by the DB seeder)."""
    matrix: dict[str, list[str]] = {canonical: [] for canonical in INGREDIENTS}
    for rule in CONFLICT_RULES:
        if rule.b not in matrix[rule.a]:
            matrix[rule.a].append(rule.b)
        if rule.a not in matrix[rule.b]:
            matrix[rule.b].append(rule.a)
    return matrix
