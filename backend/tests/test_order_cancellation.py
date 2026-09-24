from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.main import app
from app.db.base import Base
from app.models.enums import OrderStatus, UserRole
from app.models.menu_item import MenuItem
from app.models.order import Order, OrderItem
from app.models.user import User


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as session:
        session.add_all(
            [
                User(id=1, name="Student One", email="student1@example.com", password_hash="prototype-password", role=UserRole.STUDENT),
                User(id=2, name="Student Two", email="student2@example.com", password_hash="prototype-password", role=UserRole.STUDENT),
                User(id=3, name="Admin", email="admin@example.com", password_hash="prototype-password", role=UserRole.ADMIN),
                MenuItem(id=1, name="Idli", description="Steamed rice cakes.", price=Decimal("35.00"), category="Breakfast", is_available=True),
            ]
        )
        session.commit()


def teardown_function():
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def auth_headers(user_id: int):
    return {"Authorization": f"Bearer demo-user-{user_id}"}


def create_order(user_id: int, status: OrderStatus = OrderStatus.PLACED) -> int:
    with TestingSessionLocal() as session:
        item = session.scalar(select(MenuItem).where(MenuItem.id == 1))
        order = Order(user_id=user_id, total_amount=Decimal("35.00"), status=status)
        order.items.append(OrderItem(menu_item=item, quantity=1, unit_price=item.price, subtotal=item.price))
        session.add(order)
        session.commit()
        return order.id


def test_student_can_cancel_own_placed_order_and_admin_sees_status(client):
    order_id = create_order(user_id=1)

    cancel_res = client.post(f"/api/orders/{order_id}/cancel", headers=auth_headers(1))
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    with TestingSessionLocal() as session:
        assert session.get(Order, order_id).status == OrderStatus.CANCELLED

    admin_res = client.get("/api/admin/orders?status=CANCELLED", headers=auth_headers(3))
    assert admin_res.status_code == 200
    assert any(order["id"] == order_id and order["status"] == "CANCELLED" for order in admin_res.json())


def test_student_cannot_cancel_another_students_order(client):
    order_id = create_order(user_id=1)

    cancel_res = client.post(f"/api/orders/{order_id}/cancel", headers=auth_headers(2))
    assert cancel_res.status_code == 403


def test_only_placed_orders_can_be_cancelled(client):
    for status in [OrderStatus.PREPARING, OrderStatus.READY, OrderStatus.COLLECTED, OrderStatus.CANCELLED]:
        order_id = create_order(user_id=1, status=status)
        cancel_res = client.post(f"/api/orders/{order_id}/cancel", headers=auth_headers(1))
        assert cancel_res.status_code == 409
        with TestingSessionLocal() as session:
            assert session.get(Order, order_id).status == status


def test_order_creation_and_existing_status_transitions_still_work(client):
    create_res = client.post("/api/orders", json={"items": [{"menu_item_id": 1, "quantity": 1}]}, headers=auth_headers(1))
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]
    assert create_res.json()["status"] == "PLACED"

    prep_res = client.patch(f"/api/admin/orders/{order_id}/status", json={"status": "PREPARING"}, headers=auth_headers(3))
    assert prep_res.status_code == 200
    assert prep_res.json()["status"] == "PREPARING"

    ready_res = client.patch(f"/api/admin/orders/{order_id}/status", json={"status": "READY"}, headers=auth_headers(3))
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "READY"

    collected_res = client.patch(f"/api/admin/orders/{order_id}/status", json={"status": "COLLECTED"}, headers=auth_headers(3))
    assert collected_res.status_code == 200
    assert collected_res.json()["status"] == "COLLECTED"
