from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.menu import MenuItem
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu import MenuItemCreate, MenuItemUpdate


class MenuService:
    @staticmethod
    def list_menu_items(
        db: Session,
        category: str | None = None,
        available_only: bool = False,
    ) -> list[MenuItem]:
        return MenuRepository.get_all(db, category=category, available_only=available_only)

    @staticmethod
    def get_menu_item(db: Session, item_id: int) -> MenuItem:
        item = MenuRepository.get_by_id(db, item_id)
        if not item:
            raise AppError(f"Menu item with ID {item_id} not found", status_code=404)
        return item

    @staticmethod
    def create_menu_item(db: Session, data: MenuItemCreate) -> MenuItem:
        cleaned_name = data.name.strip()
        if not cleaned_name:
            raise AppError("Menu item name cannot be empty", status_code=422)
        if data.price < 0:
            raise AppError("Price must be non-negative", status_code=422)

        existing = MenuRepository.get_by_name(db, cleaned_name)
        if existing:
            raise AppError(f"A menu item named '{cleaned_name}' already exists", status_code=409)

        item = MenuItem(
            name=cleaned_name,
            description=data.description.strip() if data.description else None,
            price=float(data.price),
            category=data.category.strip() if data.category else "General",
            image_url=data.image_url.strip() if data.image_url else None,
            is_available=data.is_available,
        )
        return MenuRepository.create(db, item)

    @staticmethod
    def update_menu_item(db: Session, item_id: int, data: MenuItemUpdate) -> MenuItem:
        item = MenuService.get_menu_item(db, item_id)
        update_dict = {}

        if data.name is not None:
            cleaned_name = data.name.strip()
            if not cleaned_name:
                raise AppError("Menu item name cannot be empty", status_code=422)
            existing = MenuRepository.get_by_name(db, cleaned_name)
            if existing and existing.id != item_id:
                raise AppError(f"A menu item named '{cleaned_name}' already exists", status_code=409)
            update_dict["name"] = cleaned_name

        if data.price is not None:
            if data.price < 0:
                raise AppError("Price must be non-negative", status_code=422)
            update_dict["price"] = float(data.price)

        if data.description is not None:
            update_dict["description"] = data.description.strip() if data.description else None

        if data.category is not None:
            update_dict["category"] = data.category.strip() if data.category else "General"

        if data.image_url is not None:
            update_dict["image_url"] = data.image_url.strip() if data.image_url else None

        if data.is_available is not None:
            update_dict["is_available"] = bool(data.is_available)

        return MenuRepository.update(db, item, update_dict)

    @staticmethod
    def delete_menu_item(db: Session, item_id: int) -> None:
        item = MenuService.get_menu_item(db, item_id)
        MenuRepository.delete(db, item)

    @staticmethod
    def set_availability(db: Session, item_id: int, is_available: bool) -> MenuItem:
        item = MenuService.get_menu_item(db, item_id)
        return MenuRepository.set_availability(db, item, is_available)

    @staticmethod
    def toggle_availability(db: Session, item_id: int) -> MenuItem:
        item = MenuService.get_menu_item(db, item_id)
        return MenuRepository.set_availability(db, item, not item.is_available)

    @staticmethod
    def seed_initial_menu(db: Session) -> None:
        """Seed realistic canteen menu items if none exist."""
        existing = MenuRepository.get_all(db)
        if not existing:
            sample_items = [
                MenuItem(
                    name="Masala Dosa",
                    description="Crispy rice crepe filled with spiced potato masala, served with chutney and sambar",
                    price=60.0,
                    category="Breakfast",
                    is_available=True,
                ),
                MenuItem(
                    name="Idli Vada Combo",
                    description="Two steamed idlis and one crispy medu vada with sambar and fresh coconut chutney",
                    price=50.0,
                    category="Breakfast",
                    is_available=True,
                ),
                MenuItem(
                    name="Veg Fried Rice",
                    description="Fragrant basmati rice tossed with fresh garden vegetables and oriental sauces",
                    price=80.0,
                    category="Lunch",
                    is_available=True,
                ),
                MenuItem(
                    name="Paneer Butter Masala Meal",
                    description="Rich tomato cashew gravy with cottage cheese, served with 2 rotis and jeera rice",
                    price=110.0,
                    category="Lunch",
                    is_available=True,
                ),
                MenuItem(
                    name="Veg Samosa (2 pcs)",
                    description="Crisp golden pastry stuffed with spiced potatoes and peas, served with mint chutney",
                    price=30.0,
                    category="Snacks",
                    is_available=True,
                ),
                MenuItem(
                    name="Grilled Cheese Sandwich",
                    description="Toasted sandwich loaded with melted cheese, bell peppers, and herbs",
                    price=55.0,
                    category="Snacks",
                    is_available=False,
                ),
                MenuItem(
                    name="South Indian Filter Coffee",
                    description="Freshly brewed chicory-infused milk coffee served hot in traditional tumbler",
                    price=25.0,
                    category="Beverages",
                    is_available=True,
                ),
                MenuItem(
                    name="Cold Badam Milk",
                    description="Chilled almond flavored milk enriched with saffron and crushed nuts",
                    price=35.0,
                    category="Beverages",
                    is_available=True,
                ),
            ]
            for item in sample_items:
                MenuRepository.create(db, item)
from app.core.exceptions import AppError
from app.models.menu_item import MenuItem
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu import MenuItemCreate, MenuItemUpdate

class MenuService:
    def __init__(self, menu: MenuRepository): self.menu = menu
    def list_items(self): return self.menu.list_all()
    def create(self, data: MenuItemCreate):
        if any(item.name.lower() == data.name.lower() for item in self.menu.list_all()): raise AppError("A menu item with this name already exists", 409)
        return self.menu.create(MenuItem(**data.model_dump()))
    def update(self, item_id: int, data: MenuItemUpdate):
        item = self._item(item_id)
        for field, value in data.model_dump(exclude_unset=True).items(): setattr(item, field, value)
        return item
    def set_availability(self, item_id: int, is_available: bool):
        item = self._item(item_id); item.is_available = is_available; return item
    def delete(self, item_id: int):
        self.menu.delete(self._item(item_id))
    def _item(self, item_id: int):
        item = self.menu.get_by_id(item_id)
        if not item: raise AppError("Menu item not found", 404)
        return item
