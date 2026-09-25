from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.menu import MenuItem


class MenuRepository:
    @staticmethod
    def get_all(
        db: Session,
        category: str | None = None,
        available_only: bool = False,
    ) -> list[MenuItem]:
        stmt = select(MenuItem).order_by(MenuItem.category, MenuItem.name)
        if category:
            stmt = stmt.where(MenuItem.category == category)
        if available_only:
            stmt = stmt.where(MenuItem.is_available.is_(True))
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_by_id(db: Session, item_id: int) -> MenuItem | None:
        return db.get(MenuItem, item_id)

    @staticmethod
    def get_by_name(db: Session, name: str) -> MenuItem | None:
        stmt = select(MenuItem).where(func.lower(MenuItem.name) == func.lower(name.strip()))
        return db.scalars(stmt).first()

    @staticmethod
    def create(db: Session, item: MenuItem) -> MenuItem:
        db.add(item)
        db.flush()
        db.refresh(item)
        return item

    @staticmethod
    def update(db: Session, item: MenuItem, update_fields: dict) -> MenuItem:
        for key, value in update_fields.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        db.flush()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, item: MenuItem) -> None:
        db.delete(item)
        db.flush()

    @staticmethod
    def set_availability(db: Session, item: MenuItem, is_available: bool) -> MenuItem:
        item.is_available = is_available
        db.flush()
        db.refresh(item)
        return item

    @staticmethod
    def count_summary(db: Session) -> tuple[int, int, int]:
        total = db.scalar(select(func.count(MenuItem.id))) or 0
        available = db.scalar(select(func.count(MenuItem.id)).where(MenuItem.is_available.is_(True))) or 0
        unavailable = total - available
        return total, available, unavailable
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.menu_item import MenuItem

class MenuRepository:
    def __init__(self, session: Session): self.session = session
    def list_all(
        self,
        category: str | None = None,
        available_only: bool = False,
        search: str | None = None,
        ):
        from sqlalchemy import func
        stmt = select(MenuItem).order_by(MenuItem.category, MenuItem.name)
        if category and category.strip().lower() != "all":
            stmt = stmt.where(func.lower(MenuItem.category) == category.strip().lower())
        if available_only:
            stmt = stmt.where(MenuItem.is_available.is_(True))
        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                func.lower(MenuItem.name).like(term) | func.lower(MenuItem.description).like(term)
            )
        return list(self.session.scalars(stmt))
    def get_by_id(self, item_id: int): return self.session.get(MenuItem, item_id)
    def get_by_ids(self, ids: list[int]): return list(self.session.scalars(select(MenuItem).where(MenuItem.id.in_(ids))))
    def create(self, item: MenuItem): self.session.add(item); self.session.flush(); return item
    def delete(self, item: MenuItem): self.session.delete(item)
