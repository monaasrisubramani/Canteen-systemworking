from datetime import UTC, datetime
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.order import Order, OrderItem, OrderStatus
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.order import AdminSummaryResponse, OrderCreate


class OrderService:
    @staticmethod
    def list_orders(db: Session, status: str | None = None) -> list[Order]:
        return OrderRepository.get_all(db, status=status)

    @staticmethod
    def get_order(db: Session, order_id: int) -> Order:
        order = OrderRepository.get_by_id(db, order_id)
        if not order:
            raise AppError(f"Order #{order_id} not found", status_code=404)
        return order

    @staticmethod
    def create_order(db: Session, data: OrderCreate) -> Order:
        if not data.items:
            raise AppError("Order must contain at least one item", status_code=422)

        total = sum(item.price * item.quantity for item in data.items)
        order = Order(
            customer_name=data.customer_name.strip(),
            student_id=data.student_id.strip() if data.student_id else None,
            phone_number=data.phone_number.strip() if data.phone_number else None,
            status=OrderStatus.PENDING.value,
            total_amount=round(total, 2),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        for line in data.items:
            order_item = OrderItem(
                menu_item_id=line.menu_item_id,
                item_name=line.item_name.strip(),
                price=float(line.price),
                quantity=int(line.quantity),
            )
            order.items.append(order_item)

        return OrderRepository.create(db, order)

    @staticmethod
    def update_order_status(db: Session, order_id: int, new_status: OrderStatus) -> Order:
        order = OrderService.get_order(db, order_id)
        valid_statuses = {s.value for s in OrderStatus}
        if new_status.value not in valid_statuses:
            raise AppError(f"Invalid order status: {new_status}", status_code=422)

        order.updated_at = datetime.now(UTC)
        return OrderRepository.update_status(db, order, new_status.value)

    @staticmethod
    def get_admin_summary(db: Session) -> AdminSummaryResponse:
        order_counts = OrderRepository.count_summary(db)
        total_menu, available_menu, unavailable_menu = MenuRepository.count_summary(db)

        return AdminSummaryResponse(
            pending_orders=order_counts.get(OrderStatus.PENDING.value, 0),
            preparing_orders=order_counts.get(OrderStatus.PREPARING.value, 0),
            ready_orders=order_counts.get(OrderStatus.READY.value, 0),
            completed_orders=order_counts.get(OrderStatus.COMPLETED.value, 0),
            cancelled_orders=order_counts.get(OrderStatus.CANCELLED.value, 0),
            total_orders=order_counts.get("Total", 0),
            available_menu_items=available_menu,
            unavailable_menu_items=unavailable_menu,
            total_menu_items=total_menu,
        )

    @staticmethod
    def seed_initial_orders(db: Session) -> None:
        """Seed sample orders if table is empty for demonstration and testing."""
        existing = OrderRepository.get_all(db)
        if not existing:
            sample_orders_data = [
                {
                    "customer": "Aarav Sharma",
                    "student_id": "STU-2024-041",
                    "status": OrderStatus.PENDING.value,
                    "items": [
                        {"name": "Masala Dosa", "price": 60.0, "qty": 2},
                        {"name": "South Indian Filter Coffee", "price": 25.0, "qty": 1},
                    ],
                },
                {
                    "customer": "Priya Patel",
                    "student_id": "STU-2024-118",
                    "status": OrderStatus.PREPARING.value,
                    "items": [
                        {"name": "Veg Fried Rice", "price": 80.0, "qty": 1},
                        {"name": "Cold Badam Milk", "price": 35.0, "qty": 1},
                    ],
                },
                {
                    "customer": "Rohan Verma",
                    "student_id": "STU-2024-089",
                    "status": OrderStatus.READY.value,
                    "items": [
                        {"name": "Idli Vada Combo", "price": 50.0, "qty": 1},
                    ],
                },
                {
                    "customer": "Sneha Iyer",
                    "student_id": "STU-2024-004",
                    "status": OrderStatus.COMPLETED.value,
                    "items": [
                        {"name": "Veg Samosa (2 pcs)", "price": 30.0, "qty": 2},
                        {"name": "South Indian Filter Coffee", "price": 25.0, "qty": 2},
                    ],
                },
            ]

            for o_data in sample_orders_data:
                total = sum(i["price"] * i["qty"] for i in o_data["items"])
                order = Order(
                    customer_name=o_data["customer"],
                    student_id=o_data["student_id"],
                    status=o_data["status"],
                    total_amount=total,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
                for item_dict in o_data["items"]:
                    order.items.append(
                        OrderItem(
                            item_name=item_dict["name"],
                            price=item_dict["price"],
                            quantity=item_dict["qty"],
                        )
                    )
                OrderRepository.create(db, order)
from decimal import Decimal
from app.core.exceptions import AppError
from app.models.enums import OrderStatus
from app.models.order import Order, OrderItem
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate

class OrderService:
    def __init__(self, orders: OrderRepository, menu: MenuRepository): self.orders = orders; self.menu = menu
    def create(self, user_id: int, data: OrderCreate) -> Order:
        ids = [item.menu_item_id for item in data.items]
        if len(ids) != len(set(ids)): raise AppError("Each menu item can appear only once", 422)
        menu_by_id = {item.id: item for item in self.menu.get_by_ids(ids)}
        if len(menu_by_id) != len(ids): raise AppError("One or more menu items were not found", 404)
        unavailable = [item.name for item in menu_by_id.values() if not item.is_available]
        if unavailable: raise AppError(f"Menu item unavailable: {', '.join(unavailable)}", 409)
        order = Order(user_id=user_id, total_amount=Decimal("0.00"))
        for request_item in data.items:
            menu_item = menu_by_id[request_item.menu_item_id]
            subtotal = menu_item.price * request_item.quantity
            order.items.append(OrderItem(menu_item_id=menu_item.id, quantity=request_item.quantity, unit_price=menu_item.price, subtotal=subtotal))
            order.total_amount += subtotal
        return self.orders.create(order)
    def get_for_student(self, order_id: int, user_id: int) -> Order:
        order = self.orders.get_by_id(order_id)
        if not order: raise AppError("Order not found", 404)
        if order.user_id != user_id: raise AppError("Forbidden", 403)
        return order

    def cancel_for_student(self, order_id: int, user_id: int) -> Order:
        order = self.get_for_student(order_id, user_id)
        current_status = OrderStatus(order.status)
        if current_status != OrderStatus.PLACED:
            raise AppError("Only placed orders can be cancelled", 409)
        order.status = OrderStatus.CANCELLED
        self.orders.session.flush()
        return order
