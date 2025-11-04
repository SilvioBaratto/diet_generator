"""Diet API Pydantic schemas"""

# Import all schemas for easy access
from app.schemas.diet import (
    UserSettingsIn,
    UserSettingsOut,
    DietSummary,
    PastoSchema,
    DietaSettimanaleSchema,
    DietaConLista,
    RecipeResponse
)

# Export all schemas
__all__ = [
    "UserSettingsIn",
    "UserSettingsOut", 
    "DietSummary",
    "PastoSchema",
    "DietaSettimanaleSchema",
    "DietaConLista",
    "RecipeResponse"
]