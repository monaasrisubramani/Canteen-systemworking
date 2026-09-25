from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.dependencies import get_db, require_admin
from app.core.exceptions import AppError
from app.models.enums import OrderStatus
from app.models.menu_item import MenuItem
from app.models.order import Order, OrderItem
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.menu import AvailabilityUpdate, MenuItemCreate, MenuItemResponse, MenuItemUpdate
from app.schemas.order import (
    AdminOrderItemResponse,
    AdminOrderResponse,
    AdminSummaryResponse,
    OrderStatusUpdate,
)
from app.services.menu_service import MenuService
from app.services.order_status_service import OrderStatusService

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def _serialize_order(order: Order) -> AdminOrderResponse:
    customer_name = order.user.name if order.user else f"User #{order.user_id}"
    customer_email = order.user.email if order.user else ""
    token_code = order.token.token_code if order.token else None

    items = []
    for item in order.items:
        item_name = item.menu_item.name if item.menu_item else f"Item #{item.menu_item_id}"
        items.append(
            AdminOrderItemResponse(
                id=item.id,
                menu_item_id=item.menu_item_id,
                item_name=item_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
        )

    return AdminOrderResponse(
        id=order.id,
        user_id=order.user_id,
        customer_name=customer_name,
        customer_email=customer_email,
        total_amount=order.total_amount,
        status=order.status.value if hasattr(order.status, "value") else str(order.status),
        token_code=token_code,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=items,
    )


@router.get("/summary", response_model=AdminSummaryResponse)
def admin_summary(_: object = Depends(require_admin), db: Session = Depends(get_db)):
    orders = list(db.scalars(select(Order)))
    menu_items = list(db.scalars(select(MenuItem)))
    return AdminSummaryResponse(
        total_orders=len(orders),
        placed_orders=sum(1 for o in orders if o.status == OrderStatus.PLACED),
        preparing_orders=sum(1 for o in orders if o.status == OrderStatus.PREPARING),
        ready_orders=sum(1 for o in orders if o.status == OrderStatus.READY),
        collected_orders=sum(1 for o in orders if o.status == OrderStatus.COLLECTED),
        cancelled_orders=sum(1 for o in orders if o.status == OrderStatus.CANCELLED),
        available_menu_items=sum(1 for m in menu_items if m.is_available),
        unavailable_menu_items=sum(1 for m in menu_items if not m.is_available),
        total_menu_items=len(menu_items),
    )


@router.get("/menu", response_model=list[MenuItemResponse])
def menu(
    category: str | None = Query(default=None),
    available_only: bool = Query(default=False),
    search: str | None = Query(default=None),
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return MenuService(MenuRepository(db)).list_items(
        category=category,
        available_only=available_only,
        search=search,
    )


@router.post("/menu", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu(data: MenuItemCreate, _: object = Depends(require_admin), db: Session = Depends(get_db)):
    return MenuService(MenuRepository(db)).create(data)


@router.put("/menu/{item_id}", response_model=MenuItemResponse)
@router.patch("/menu/{item_id}", response_model=MenuItemResponse)
def update_menu(item_id: int, data: MenuItemUpdate, _: object = Depends(require_admin), db: Session = Depends(get_db)):
    return MenuService(MenuRepository(db)).update(item_id, data)


@router.patch("/menu/{item_id}/availability", response_model=MenuItemResponse)
def update_availability(item_id: int, data: AvailabilityUpdate, _: object = Depends(require_admin), db: Session = Depends(get_db)):
    return MenuService(MenuRepository(db)).set_availability(item_id, data.is_available)


@router.delete("/menu/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(item_id: int, _: object = Depends(require_admin), db: Session = Depends(get_db)):
    MenuService(MenuRepository(db)).delete(item_id)


@router.get("/orders", response_model=list[AdminOrderResponse])
def admin_orders(
    status: str | None = Query(default=None),
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.token),
            selectinload(Order.items).selectinload(OrderItem.menu_item),
        )
        .order_by(Order.created_at.desc())
    )
    if status and status.strip().upper() != "ALL":
        norm = status.strip().upper()
        mapping = {
            "PENDING": OrderStatus.PLACED,
            "COMPLETED": OrderStatus.COLLECTED,
        }
        status_val = mapping.get(norm)
        if not status_val:
            try:
                status_val = OrderStatus(norm)
            except ValueError:
                status_val = None
        if status_val:
            stmt = stmt.where(Order.status == status_val)

    orders = list(db.scalars(stmt))
    return [_serialize_order(o) for o in orders]


@router.get("/orders/{order_id}", response_model=AdminOrderResponse)
def admin_order(order_id: int, _: object = Depends(require_admin), db: Session = Depends(get_db)):
    stmt = (
        select(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.token),
            selectinload(Order.items).selectinload(OrderItem.menu_item),
        )
        .where(Order.id == order_id)
    )
    order = db.scalar(stmt)
    if not order:
        raise AppError("Order not found", 404)
    return _serialize_order(order)


@router.patch("/orders/{order_id}/status", response_model=AdminOrderResponse)
def update_status(
    order_id: int,
    data: OrderStatusUpdate,
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
):
    norm = data.status.strip().upper()
    mapping = {
        "PENDING": OrderStatus.PLACED,
        "COMPLETED": OrderStatus.COLLECTED,
    }
    target_status = mapping.get(norm, norm)
    OrderStatusService(OrderRepository(db)).update(order_id, target_status)
    db.flush()

    stmt = (
        select(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.token),
            selectinload(Order.items).selectinload(OrderItem.menu_item),
        )
        .where(Order.id == order_id)
    )
    order = db.scalar(stmt)
    return _serialize_order(order)
