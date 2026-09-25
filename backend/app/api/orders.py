from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_staff
from app.models.user import User
from app.schemas.order import (
    AdminSummaryResponse,
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/api", tags=["Orders & Administration"])


@router.get("/orders", response_model=list[OrderResponse])
def get_orders(
    status: str | None = Query(None, description="Filter orders by status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
) -> list[OrderResponse]:
    """List incoming orders for canteen staff. Requires staff authorization."""
    return OrderService.list_orders(db, status=status)


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
) -> OrderResponse:
    """Retrieve detailed order information. Requires staff authorization."""
    return OrderService.get_order(db, order_id)


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
) -> OrderResponse:
    """Update order processing status. Requires staff authorization."""
    return OrderService.update_order_status(db, order_id, payload.status)


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
) -> OrderResponse:
    """Place a new order. Open endpoint for student/customer flows."""
    return OrderService.create_order(db, payload)


@router.get("/admin/summary", response_model=AdminSummaryResponse)
def get_admin_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
) -> AdminSummaryResponse:
    """Get canteen operational summary metrics. Requires staff authorization."""
    return OrderService.get_admin_summary(db)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_db
from app.models.enums import PaymentStatus
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderItemResponse, OrderResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/orders", tags=["Orders"])

def serialize(order):
    items = [
        OrderItemResponse(
            id=item.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
        )
        for item in order.items
    ]
    latest_payment = order.payments[-1] if hasattr(order, "payments") and order.payments else None
    has_success_payment = any(p.status == PaymentStatus.SUCCESS for p in order.payments) if hasattr(order, "payments") and order.payments else False
    payment_status = "SUCCESS" if has_success_payment else (latest_payment.status.value if latest_payment else "UNPAID")
    token_code = order.token.token_code if hasattr(order, "token") and order.token else None
    transaction_ref = latest_payment.transaction_reference if latest_payment else None
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        total_amount=order.total_amount,
        status=order.status.value if hasattr(order.status, "value") else str(order.status),
        payment_status=payment_status,
        token_code=token_code,
        transaction_reference=transaction_ref,
        created_at=order.created_at,
        items=items,
    )

@router.post("", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return serialize(OrderService(OrderRepository(db), MenuRepository(db)).create(user.id, data))

@router.get("", response_model=list[OrderResponse])
def list_orders(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return [serialize(order) for order in OrderRepository(db).list_for_user(user.id)]

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return serialize(OrderService(OrderRepository(db), MenuRepository(db)).get_for_student(order_id, user.id))

@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    order = OrderService(OrderRepository(db), MenuRepository(db)).cancel_for_student(order_id, user.id)
    return serialize(order)
