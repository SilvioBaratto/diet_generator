"""Diet API endpoints"""

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_current_user
from app.database import get_db
from app.services import DietService
from app.schemas import DietSummary, DietaConLista
from app.schemas.diet import DietaSettimanaleSchema
from baml_client.types import ListaSpesa as ListaSpesaSchema

router = APIRouter(prefix="/diet", tags=["diet"])


@router.get(
    "/list",
    response_model=List[DietSummary],
    summary="List all weekly diets for the current user",
)
def list_user_diets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get all diets for the current user"""
    user_id = current_user["id"]
    diet_service = DietService(db)
    return diet_service.get_user_diets(user_id)


@router.get(
    "/current_week",
    response_model=Optional[DietaConLista],
    summary="Retrieve the weekly diet plan + grocery list for the current week",
)
def get_current_week_diet(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get the diet plan for the current week. Returns null if no diet exists for this week."""
    user_id = current_user["id"]
    diet_service = DietService(db)
    return diet_service.get_current_week_diet(user_id)


@router.post(
    "/create_diet",
    response_model=DietaConLista,
    summary="Generate, save, and return a weekly diet plan + grocery list based on the user's saved settings",
)
async def create_diet(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new weekly diet plan with grocery list"""
    user_id = current_user["id"]
    diet_service = DietService(db)
    return await diet_service.create_diet(user_id)


@router.get(
    "/{diet_id}",
    response_model=DietaSettimanaleSchema,
    summary="Retrieve a full weekly diet by its ID (no shopping list)",
)
def get_diet_by_id(
    diet_id: str = Path(..., description="The UUID of the weekly diet"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific diet by ID"""
    user_id = current_user["id"]
    diet_service = DietService(db)
    return diet_service.get_diet_by_id(diet_id, user_id)


@router.get(
    "/{diet_id}/grocery-list",
    response_model=ListaSpesaSchema,
    summary="Retrieve the grocery list for a specific diet",
)
def get_diet_grocery_list(
    diet_id: str = Path(..., description="The UUID of the weekly diet"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get grocery list with ingredients, quantities, and units for a specific diet"""
    user_id = current_user["id"]
    diet_service = DietService(db)
    return diet_service.get_grocery_list_by_diet_id(diet_id, user_id)