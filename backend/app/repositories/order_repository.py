from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem, OrderStatus


class OrderRepository:
    @staticmethod
    def get_all(db: Session, status: str | None = None) -> list[Order]:
        stmt = select(Order).order_by(Order.created_at.desc())
        if status:
            stmt = stmt.where(Order.status == status)
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_by_id(db: Session, order_id: int) -> Order | None:
        return db.get(Order, order_id)

    @staticmethod
    def create(db: Session, order: Order) -> Order:
        db.add(order)
        db.flush()
        db.refresh(order)
        return order

    @staticmethod
    def update_status(db: Session, order: Order, new_status: str) -> Order:
        order.status = new_status
        db.flush()
        db.refresh(order)
        return order

    @staticmethod
    def count_summary(db: Session) -> dict[str, int]:
        counts = {s.value: 0 for s in OrderStatus}
        stmt = select(Order.status, func.count(Order.id)).group_by(Order.status)
        results = db.execute(stmt).all()
        for status_val, count in results:
            counts[status_val] = count
        counts["Total"] = sum(counts[s.value] for s in OrderStatus)
        return counts
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.models.order import Order

class OrderRepository:
    def __init__(self, session: Session): self.session = session
    def get_by_id(self, order_id: int):
        return self.session.scalar(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.payments),
                selectinload(Order.token),
            )
            .where(Order.id == order_id)
        )
    def list_for_user(self, user_id: int):
        return list(
            self.session.scalars(
                select(Order)
                .options(
                    selectinload(Order.items),
                    selectinload(Order.payments),
                    selectinload(Order.token),
                )
                .where(Order.user_id == user_id)
                .order_by(Order.created_at.desc())
            )
        )
    def create(self, order: Order): self.session.add(order); self.session.flush(); return order
