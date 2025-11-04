"""Meal service for business logic operations"""

import logging
from typing import List, cast, Literal

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import MealType
from app.repositories import MealRepository
from baml_client.async_client import b
from baml_client.types import (
    Pasto as PastoSchema,
    TipoPasto as TipoPastoSchema,
    Ingrediente as IngredienteSchema,
    HtmlStructure,
)

logger = logging.getLogger(__name__)

# Type alias for meal type literals
MealTypeLiteral = Literal['colazione', 'pranzo', 'cena', 'spuntino']


class MealService:
    """Service class for meal-related business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.meal_repo = MealRepository(db)
    
    def get_meal_details(self, meal_id: str, user_id: str) -> PastoSchema:
        """Get detailed meal information"""
        meal = self.meal_repo.get_with_ingredients(meal_id)

        if not meal:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Meal not found.")

        # Ensure it belongs to the current user
        if meal.weekly_diet.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have access to that meal.")

        # Map back to Italian literals
        inv_type_map = {
            MealType.BREAKFAST: "colazione",
            MealType.LUNCH: "pranzo",
            MealType.DINNER: "cena",
            MealType.SNACK: "spuntino",
        }

        tp = TipoPastoSchema(
            tipo=cast(MealTypeLiteral, inv_type_map[meal.meal_type]),
            orario=meal.time,
            ricetta=meal.recipe or "",
        )

        ingredients = [
            IngredienteSchema(
                nome=mi.ingredient.name,
                quantita=mi.quantity,
                unita=mi.ingredient.unit,
            )
            for mi in meal.ingredients
        ]

        return PastoSchema(
            tipoPasto=tp,
            ingredienti=ingredients,
            calorie=meal.calories,
        )
    
    async def get_meal_recipe(self, meal_id: str, user_id: str) -> HtmlStructure:
        """Generate full recipe for a meal"""
        meal = self.meal_repo.get_with_ingredients(meal_id)
        
        if not meal:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Meal not found.")

        if meal.weekly_diet.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have access to that meal.")

        # Reverse-map enum to Italian literal
        inv_type_map = {
            MealType.BREAKFAST: "colazione",
            MealType.LUNCH: "pranzo",
            MealType.DINNER: "cena",
            MealType.SNACK: "spuntino",
        }

        tp = TipoPastoSchema(
            tipo=cast(MealTypeLiteral, inv_type_map[meal.meal_type]),
            orario=meal.time,
            ricetta=meal.recipe or "",
        )
        
        ings: List[IngredienteSchema] = [
            IngredienteSchema(
                nome=mi.ingredient.name,
                quantita=mi.quantity,
                unita=mi.ingredient.unit,
            )
            for mi in meal.ingredients
        ]
        
        pasto = PastoSchema(
            tipoPasto=tp,
            ingredienti=ings,
            calorie=meal.calories,
        )

        try:
            full_recipe: HtmlStructure = await b.GeneraRicetta(pasto)
        except Exception as e:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                f"Failed to generate recipe: {e}"
            )

        return full_recipe