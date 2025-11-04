"""Database models for Diet API"""

# Import base classes
from app.models.base import Base

# Import all models for easy access
from app.models.diet import (
    User,
    WeeklyDiet,
    Meal,
    Ingredient,
    MealIngredient,
    GroceryList,
    GroceryListItem,
    UserSettings,
    MealType
)

# Export all models
__all__ = [
    "Base",
    "User",
    "WeeklyDiet", 
    "Meal",
    "Ingredient",
    "MealIngredient",
    "GroceryList",
    "GroceryListItem",
    "UserSettings",
    "MealType"
]