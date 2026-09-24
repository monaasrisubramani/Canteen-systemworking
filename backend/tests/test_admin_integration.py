from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_admin_login_and_auth_flow():
    # Test invalid login
    res = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "wrongpassword"})
    assert res.status_code == 401

    # Test login with email & prototype password
    res = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "prototype-password"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "ADMIN"
    token = data["access_token"]

    # Test login with username "admin" & "admin123"
    res2 = client.post("/api/auth/login", json={"email": "admin", "password": "admin123"})
    assert res2.status_code == 200
    assert res2.json()["user"]["role"] == "ADMIN"

    # Test /api/auth/me with admin token
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["role"] == "ADMIN"
    assert res_me.json()["email"] == "admin@example.com"

    # Test /api/auth/me with invalid token
    res_bad = client.get("/api/auth/me", headers={"Authorization": "Bearer bad-token"})
    assert res_bad.status_code == 401


def test_role_authorization_protection():
    # Student login
    res = client.post("/api/auth/login", json={"email": "student@example.com", "password": "prototype-password"})
    assert res.status_code == 200
    student_token = res.json()["access_token"]

    # Student trying to access admin summary -> 403 Forbidden
    res_sum = client.get("/api/admin/summary", headers={"Authorization": f"Bearer {student_token}"})
    assert res_sum.status_code == 403

    # Student trying to access admin menu -> 403
    res_menu = client.get("/api/admin/menu", headers={"Authorization": f"Bearer {student_token}"})
    assert res_menu.status_code == 403

    # Student trying to access admin orders -> 403
    res_ord = client.get("/api/admin/orders", headers={"Authorization": f"Bearer {student_token}"})
    assert res_ord.status_code == 403


def test_admin_summary_metrics():
    res = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "prototype-password"})
    admin_token = res.json()["access_token"]

    res_sum = client.get("/api/admin/summary", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_sum.status_code == 200
    summary = res_sum.json()
    assert "total_orders" in summary
    assert "placed_orders" in summary
    assert "preparing_orders" in summary
    assert "ready_orders" in summary
    assert "collected_orders" in summary
    assert "available_menu_items" in summary
    assert "unavailable_menu_items" in summary
    assert "total_menu_items" in summary
    assert summary["total_menu_items"] == summary["available_menu_items"] + summary["unavailable_menu_items"]


def test_menu_management_crud_and_availability():
    res = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "prototype-password"})
    admin_token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create a new menu item
    new_item_payload = {
        "name": "Integration Test Biryani",
        "description": "Fragrant basmati rice cooked with authentic spices.",
        "price": 120.00,
        "category": "Lunch",
        "is_available": True,
    }
    create_res = client.post("/api/admin/menu", json=new_item_payload, headers=headers)
    assert create_res.status_code == 201
    item = create_res.json()
    item_id = item["id"]
    assert item["name"] == "Integration Test Biryani"
    assert item["is_available"] is True

    # 2. Update the menu item (PUT/PATCH)
    update_payload = {
        "name": "Integration Test Biryani Special",
        "price": 135.00,
        "category": "Lunch",
        "description": "Special chef biryani recipe.",
    }
    put_res = client.put(f"/api/admin/menu/{item_id}", json=update_payload, headers=headers)
    assert put_res.status_code == 200
    updated_item = put_res.json()
    assert updated_item["name"] == "Integration Test Biryani Special"
    assert float(updated_item["price"]) == 135.00

    # 3. Toggle availability to False (Kitchen marks item Out of Stock)
    toggle_res = client.patch(
        f"/api/admin/menu/{item_id}/availability",
        json={"is_available": False},
        headers=headers,
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_available"] is False

    # 4. Verify student checkout is BLOCKED when item is unavailable
    student_res = client.post("/api/auth/login", json={"email": "student@example.com", "password": "prototype-password"})
    student_token = student_res.json()["access_token"]
    order_res = client.post(
        "/api/orders",
        json={"items": [{"menu_item_id": item_id, "quantity": 1}]},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    # Unavailable items cannot be ordered
    assert order_res.status_code in [400, 409, 422]

    # 5. Toggle availability back to True
    toggle_on_res = client.patch(
        f"/api/admin/menu/{item_id}/availability",
        json={"is_available": True},
        headers=headers,
    )
    assert toggle_on_res.status_code == 200
    assert toggle_on_res.json()["is_available"] is True

    # 6. Delete the menu item
    del_res = client.delete(f"/api/admin/menu/{item_id}", headers=headers)
    assert del_res.status_code == 204


def test_incoming_orders_workflow_and_lifecycle():
    # Login student to place an order
    student_res = client.post("/api/auth/login", json={"email": "student@example.com", "password": "prototype-password"})
    student_token = student_res.json()["access_token"]

    # Fetch public menu to find an available item
    menu_res = client.get("/api/menu")
    available_items = [i for i in menu_res.json() if i["is_available"]]
    assert len(available_items) > 0
    target_item = available_items[0]

    # Place an order
    order_create_res = client.post(
        "/api/orders",
        json={"items": [{"menu_item_id": target_item["id"], "quantity": 2}]},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert order_create_res.status_code in [200, 201]
    order_id = order_create_res.json()["id"]

    # Admin checks incoming orders
    admin_res = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "prototype-password"})
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    list_res = client.get("/api/admin/orders?status=PLACED", headers=admin_headers)
    assert list_res.status_code == 200
    orders = list_res.json()
    placed_order = next((o for o in orders if o["id"] == order_id), None)
    assert placed_order is not None
    assert placed_order["customer_name"] == "Demo Student"
    assert len(placed_order["items"]) > 0
    assert placed_order["status"] == "PLACED"

    # Step 1: PLACED -> PREPARING
    prep_res = client.patch(
        f"/api/admin/orders/{order_id}/status",
        json={"status": "PREPARING"},
        headers=admin_headers,
    )
    assert prep_res.status_code == 200
    assert prep_res.json()["status"] == "PREPARING"

    # Invalid jump: PREPARING -> COLLECTED should fail with 409
    invalid_res = client.patch(
        f"/api/admin/orders/{order_id}/status",
        json={"status": "COLLECTED"},
        headers=admin_headers,
    )
    assert invalid_res.status_code == 409

    # Step 2: PREPARING -> READY
    ready_res = client.patch(
        f"/api/admin/orders/{order_id}/status",
        json={"status": "READY"},
        headers=admin_headers,
    )
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "READY"

    # Step 3: READY -> COLLECTED
    collected_res = client.patch(
        f"/api/admin/orders/{order_id}/status",
        json={"status": "COLLECTED"},
        headers=admin_headers,
    )
    assert collected_res.status_code == 200
    assert collected_res.json()["status"] == "COLLECTED"
