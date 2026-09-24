"""
Valid order-status transition rules.

The OrderStatus enum itself already lives in app/models/enums.py
(shared with UserRole, PaymentMethod, PaymentStatus, TokenStatus) —
this file only adds the transition logic for SCRUM-22.
"""

from app.models.enums import OrderStatus

VALID_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PLACED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING: {OrderStatus.READY, OrderStatus.CANCELLED},
    OrderStatus.READY: {OrderStatus.COLLECTED},
    OrderStatus.COLLECTED: set(),
    OrderStatus.CANCELLED: set(),
}


def is_valid_transition(current: OrderStatus, target: OrderStatus) -> bool:
    return target in VALID_TRANSITIONS.get(current, set())
