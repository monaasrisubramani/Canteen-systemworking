"""
OrderStatusService
-------------------
Business rules for changing an order's status (SCRUM-22).
"""

from app.core.exceptions import AppError
from app.models.enums import OrderStatus
from app.models.order_status import is_valid_transition


class OrderStatusService:
    def __init__(self, order_repository):
        self.order_repository = order_repository

    def update(self, order_id: int, target_status):
        order = self.order_repository.get_by_id(order_id)
        if order is None:
            raise AppError("Order not found", 404)

        try:
            target = (
                target_status
                if isinstance(target_status, OrderStatus)
                else OrderStatus(target_status)
            )
        except ValueError:
            raise AppError(f"Invalid status: {target_status}", 400)

        current = OrderStatus(order.status)

        if not is_valid_transition(current, target):
            raise AppError(
                f"Cannot move order from {current.value} to {target.value}", 400
            )

        order.status = target
        return order
