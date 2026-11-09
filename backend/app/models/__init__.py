"""SQLAlchemy models (infrastructure layer).

Importing this package registers every table on ``Base.metadata``.
"""

from app.models.base import Base
from app.models.inci_ingredient import INCIIngredient
from app.models.product import Product
from app.models.routine_log import RoutineLog
from app.models.skin_evolution_log import SkinEvolutionLog
from app.models.skin_profile import SkinProfile
from app.models.user import User

__all__ = [
    "Base",
    "INCIIngredient",
    "Product",
    "RoutineLog",
    "SkinEvolutionLog",
    "SkinProfile",
    "User",
]
