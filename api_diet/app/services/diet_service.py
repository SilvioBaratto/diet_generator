"""Diet service for business logic operations"""

import logging
import uuid
from datetime import date
from typing import List, Dict, Any, cast, Literal

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import MealType
from app.repositories import DietRepository, MealRepository, IngredientRepository, MealIngredientRepository, GroceryListRepository, GroceryListItemRepository, UserSettingsRepository
from app.schemas import DietSummary, DietaConLista
from baml_client.async_client import b
from baml_client.types import (
    DietaSettimanale as DietaSettimanaleBAML,
    Pasto as PastoBAML,
    TipoPasto as TipoPastoBAML,
    Ingrediente as IngredienteBAML,
    ListaSpesa as ListaSpesaBAML,
    TipoPasto as TipoPastoSchema,
    Ingrediente as IngredienteSchema,
    ListaSpesa as ListaSpesaSchema,
)

logger = logging.getLogger(__name__)

# Type alias for meal type literals
MealTypeLiteral = Literal['colazione', 'pranzo', 'cena', 'spuntino']


class DietService:
    """Service class for diet-related business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.diet_repo = DietRepository(db)
        self.meal_repo = MealRepository(db)
        self.ingredient_repo = IngredientRepository(db)
        self.meal_ingredient_repo = MealIngredientRepository(db)
        self.grocery_list_repo = GroceryListRepository(db)
        self.grocery_list_item_repo = GroceryListItemRepository(db)
        self.user_settings_repo = UserSettingsRepository(db)
    
    def get_user_diets(self, user_id: str) -> List[DietSummary]:
        """Get all diets for a user"""
        diets = self.diet_repo.get_user_diets(user_id)
        return [
            DietSummary(
                id=diet.id,
                name=diet.name,
                created_at=diet.created_at
            )
            for diet in diets
        ]
    
    def get_diet_by_id(self, diet_id: str, user_id: str):
        """Get full diet by ID"""
        from app.schemas.diet import PastoSchema

        weekly = self.diet_repo.get_with_meals(diet_id, user_id)

        if not weekly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diet not found."
            )

        # Map meals to PastoSchema
        inv_type_map = {
            MealType.BREAKFAST: "colazione",
            MealType.LUNCH: "pranzo",
            MealType.DINNER: "cena",
            MealType.SNACK: "spuntino",
        }

        pasti: List[PastoSchema] = []
        for m in weekly.meals:
            tp = TipoPastoSchema(
                tipo=cast(MealTypeLiteral, inv_type_map[m.meal_type]),
                orario=m.time,
                ricetta=m.recipe or "",
            )
            ings = [
                IngredienteSchema(
                    nome=mi.ingredient.name,
                    quantita=mi.quantity,
                    unita=mi.ingredient.unit,
                )
                for mi in m.ingredients
            ]

            pasti.append(
                PastoSchema(
                    id=m.id,
                    tipoPasto=tp,
                    ingredienti=ings,
                    calorie=m.calories,
                    day=m.day,
                )
            )
        
        from app.schemas.diet import DietaSettimanaleSchema
        return DietaSettimanaleSchema(
            nome=weekly.name,
            dataInizio=weekly.start_date.isoformat(),
            dataFine=weekly.end_date.isoformat(),
            pasti=pasti,
        )
    
    async def create_diet(self, user_id: str) -> DietaConLista:
        """Create a new weekly diet with grocery list"""
        from app.schemas.diet import PastoSchema

        # Load user settings
        settings = self.user_settings_repo.get_by_user_id(user_id)
        if not settings:
            raise HTTPException(404, "User settings not found.")
        if settings.weight is None or settings.height is None:
            raise HTTPException(400, "Weight and height must be set.")

        # Generate diet and grocery list using BAML
        try:
            external = await b.GeneraDietaSettimanale(
                dataInizio=date.today().isoformat(), 
                peso=settings.weight,
                altezza=settings.height,
                obiettivo=settings.goals or "",
                altri_dati=settings.other_data or "",
            )
            grocery = await b.GeneraListaSpesa(external.pasti)
        except Exception as e:
            logger.exception("Error generating diet")
            raise HTTPException(502, f"Generation failed: {e}")

        # Save WeeklyDiet
        weekly = self.diet_repo.create_diet(
            user_id=user_id,
            diet_id=str(uuid.uuid4()),
            start_date=date.fromisoformat(external.dataInizio),
            end_date=date.fromisoformat(external.dataFine),
            name=external.nome,
        )

        # Map meal types
        type_map = {
            "colazione": MealType.BREAKFAST,
            "pranzo": MealType.LUNCH,
            "cena": MealType.DINNER,
            "spuntino": MealType.SNACK,
        }

        # Save meals and ingredients
        # Group meals by type for proper distribution
        meals_by_type = {}
        for pasto in external.pasti:
            mt = pasto.tipoPasto.tipo
            if mt not in type_map:
                raise HTTPException(500, f"Unknown meal type: {mt}")
            
            if mt not in meals_by_type:
                meals_by_type[mt] = []
            meals_by_type[mt].append(pasto)

        # Distribute meals across the week (7 days)
        for meal_type, pasti_list in meals_by_type.items():
            for idx, pasto in enumerate(pasti_list):
                # Cycle through days 0-6 (Mon-Sun)
                day = idx % 7
                
                meal = self.meal_repo.create_meal(
                    meal_id=str(uuid.uuid4()),
                    weekly_diet_id=weekly.id,
                    meal_type=type_map[meal_type],
                    day=day,
                    time=pasto.tipoPasto.orario,
                    recipe=pasto.tipoPasto.ricetta,
                    calories=pasto.calorie,
                )

                # Save ingredients for this meal
                for ingr in pasto.ingredienti:
                    existing_ingr = self.ingredient_repo.get_by_name(ingr.nome)

                    if not existing_ingr:
                        existing_ingr = self.ingredient_repo.create_ingredient(
                            ingredient_id=str(uuid.uuid4()),
                            name=ingr.nome,
                            unit=ingr.unita,
                        )

                    self.meal_ingredient_repo.create_meal_ingredient(
                        meal_ingredient_id=str(uuid.uuid4()),
                        meal_id=meal.id,
                        ingredient_id=existing_ingr.id,
                        quantity=ingr.quantita,
                    )

        # Save grocery list
        grocery_list = self.grocery_list_repo.create_grocery_list(
            grocery_list_id=str(uuid.uuid4()),
            weekly_diet_id=weekly.id
        )

        for ingr in grocery.ingredienti:
            existing_ingr = self.ingredient_repo.get_by_name(ingr.nome)
            if existing_ingr:
                self.grocery_list_item_repo.create_grocery_item(
                    item_id=str(uuid.uuid4()),
                    grocery_list_id=grocery_list.id,
                    ingredient_id=existing_ingr.id,
                    quantity=ingr.quantita,
                )

        # Commit all changes
        self.db.commit()

        # Reload saved data
        saved = self.diet_repo.get_with_meals(weekly.id, user_id)

        if not saved:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reload created diet"
            )

        # Map response meals
        inv_type_map = {
            MealType.BREAKFAST: "colazione",
            MealType.LUNCH: "pranzo",
            MealType.DINNER: "cena",
            MealType.SNACK: "spuntino",
        }

        response_meals: List[PastoSchema] = []
        logger.debug(f"Converting {len(saved.meals)} meals from database to API schema")
        for m in saved.meals:
            response_meals.append(
                PastoSchema(
                    id=m.id,  # Add the missing id field
                    tipoPasto=TipoPastoSchema(
                        tipo=cast(MealTypeLiteral, inv_type_map[m.meal_type]),
                        orario=m.time,
                        ricetta=m.recipe or "",
                    ),
                    ingredienti=[
                        IngredienteSchema(
                            nome=mi.ingredient.name,
                            quantita=mi.quantity,
                            unita=mi.ingredient.unit,
                        )
                        for mi in m.ingredients
                    ],
                    calorie=m.calories,
                    day=m.day,
                )
            )

        # Convert BAML grocery list to API schema
        grocery_schema = ListaSpesaSchema(
            ingredienti=[
                IngredienteSchema(
                    nome=ingr.nome,
                    quantita=ingr.quantita,
                    unita=ingr.unita
                )
                for ingr in grocery.ingredienti
            ]
        )

        from app.schemas.diet import DietaSettimanaleSchema as DietaSettimanaleSchemaLocal
        return DietaConLista(
            dieta=DietaSettimanaleSchemaLocal(
                nome=saved.name,
                dataInizio=saved.start_date.isoformat(),
                dataFine=saved.end_date.isoformat(),
                pasti=response_meals,
            ),
            listaSpesa=grocery_schema,
        )
    
    def get_current_week_diet(self, user_id: str) -> DietaConLista | None:
        """Get current week's diet with grocery list. Returns None if no diet exists."""
        from app.schemas.diet import PastoSchema

        today = date.today()
        logger.debug(f"Looking for diet for user {user_id} on date {today}")
        weekly = self.diet_repo.get_current_week_diet(user_id, today)

        if not weekly:
            # Debug: check if user has any diets at all
            all_diets = self.diet_repo.get_user_diets(user_id)
            logger.debug(f"User has {len(all_diets)} total diets")
            for diet in all_diets:
                logger.debug(f"Diet {diet.id}: {diet.start_date} to {diet.end_date}")

            # Return None instead of raising an error - having no diet is a normal state
            logger.info(f"No diet found for user {user_id} for the current week - this is normal")
            return None

        # Build meals
        inv_type_map = {
            MealType.BREAKFAST: "colazione",
            MealType.LUNCH: "pranzo",
            MealType.DINNER: "cena",
            MealType.SNACK: "spuntino",
        }
        
        response_meals: List[PastoSchema] = []
        for m in weekly.meals:
            response_meals.append(
                PastoSchema(
                    id=m.id,
                    tipoPasto=TipoPastoSchema(
                        tipo=cast(MealTypeLiteral, inv_type_map[m.meal_type]),
                        orario=m.time,
                        ricetta=m.recipe or "",
                    ),
                    ingredienti=[
                        IngredienteSchema(
                            nome=mi.ingredient.name,
                            quantita=mi.quantity,
                            unita=mi.ingredient.unit,
                        )
                        for mi in m.ingredients
                    ],
                    calorie=m.calories,
                    day=m.day,
                )
            )

        # Build grocery list
        items: List[IngredienteSchema] = []
        if weekly.grocery_list and weekly.grocery_list.items:
            for gi in weekly.grocery_list.items:
                items.append(
                    IngredienteSchema(
                        nome=gi.ingredient.name,
                        quantita=gi.quantity,
                        unita=gi.ingredient.unit,
                    )
                )
        else:
            # Fallback: aggregate from meals
            agg: Dict[tuple[str, str], float] = {}
            for m in weekly.meals:
                for mi in m.ingredients:
                    key = (mi.ingredient.name, mi.ingredient.unit)
                    agg[key] = agg.get(key, 0.0) + mi.quantity

            for (name, unit), qty in sorted(agg.items(), key=lambda x: x[0][0]):
                items.append(IngredienteSchema(nome=name, quantita=qty, unita=unit))

        from app.schemas.diet import DietaSettimanaleSchema as DietaSettimanaleSchemaLocal2
        return DietaConLista(
            dieta=DietaSettimanaleSchemaLocal2(
                nome=weekly.name,
                dataInizio=weekly.start_date.isoformat(),
                dataFine=weekly.end_date.isoformat(),
                pasti=response_meals,
            ),
            listaSpesa=ListaSpesaSchema(ingredienti=items),
        )
    
    def get_grocery_list_by_diet_id(self, diet_id: str, user_id: str) -> ListaSpesaSchema:
        """Get grocery list for a specific diet by ID"""
        weekly = self.diet_repo.get_with_grocery_list(diet_id, user_id)
        
        if not weekly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diet not found."
            )
        
        if not weekly.grocery_list or not weekly.grocery_list.items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No grocery list found for this diet."
            )
        
        # Build grocery list items
        items = []
        for gi in weekly.grocery_list.items:
            items.append(
                IngredienteSchema(
                    nome=gi.ingredient.name,
                    quantita=gi.quantity,
                    unita=gi.ingredient.unit
                )
            )
        
        return ListaSpesaSchema(ingredienti=items)