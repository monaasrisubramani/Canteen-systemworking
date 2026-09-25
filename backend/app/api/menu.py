from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu import MenuItemResponse
from app.services.menu_service import MenuService

router = APIRouter(prefix="/api/menu", tags=["Menu"])


@router.get("", response_model=list[MenuItemResponse])
def list_menu(
    category: str | None = Query(default=None),
    available_only: bool = Query(default=False),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return MenuService(MenuRepository(db)).list_items(
        category=category,
        available_only=available_only,
        search=search,
    )