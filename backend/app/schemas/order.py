from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    menu_item_id: int | None = None
    item_name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., ge=0.0)
    quantity: int = Field(1, ge=1)


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int | None
    item_name: str
    price: float
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100)
    student_id: str | None = Field(None, max_length=50)
    phone_number: str | None = Field(None, max_length=20)
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    student_id: str | None
    phone_number: str | None
    status: str
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class AdminSummaryResponse(BaseModel):
    pending_orders: int
    preparing_orders: int
    ready_orders: int
    completed_orders: int
    cancelled_orders: int
    total_orders: int
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class OrderItemRequest(BaseModel):
    menu_item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=20)


class OrderCreate(BaseModel):
    items: list[OrderItemRequest] = Field(min_length=1, max_length=20)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    menu_item_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    total_amount: Decimal
    status: str
    items: list[OrderItemResponse]


class OrderStatusUpdate(BaseModel):
    status: str


class AdminOrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    menu_item_id: int
    item_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class AdminOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    customer_name: str
    customer_email: str
    total_amount: Decimal
    status: str
    token_code: str | None = None
    created_at: datetime
    updated_at: datetime
    items: list[AdminOrderItemResponse]


class AdminSummaryResponse(BaseModel):
    total_orders: int
    placed_orders: int
    preparing_orders: int
    ready_orders: int
    collected_orders: int
    cancelled_orders: int
    available_menu_items: int
    unavailable_menu_items: int
    total_menu_items: int
