def test_place_and_manage_orders(client, admin_token):
    # Place an order
    order_payload = {
        "customer_name": "Divya Krishnan",
        "student_id": "STU-2024-501",
        "phone_number": "9876543210",
        "items": [
            {"item_name": "Masala Dosa", "price": 60.0, "quantity": 2},
            {"item_name": "Filter Coffee", "price": 25.0, "quantity": 1},
        ],
    }
    create_res = client.post("/api/orders", json=order_payload)
    assert create_res.status_code == 201
    order_data = create_res.json()
    order_id = order_data["id"]
    assert order_data["customer_name"] == "Divya Krishnan"
    assert order_data["total_amount"] == 145.0
    assert order_data["status"] == "Pending"
    assert len(order_data["items"]) == 2

    # Staff lists orders
    list_res = client.get("/api/orders", headers={"Authorization": f"Bearer {admin_token}"})
    assert list_res.status_code == 200
    orders = list_res.json()
    assert any(o["id"] == order_id for o in orders)

    # Transition to Preparing
    prep_res = client.patch(
        f"/api/orders/{order_id}/status",
        json={"status": "Preparing"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert prep_res.status_code == 200
    assert prep_res.json()["status"] == "Preparing"

    # Transition to Ready
    ready_res = client.patch(
        f"/api/orders/{order_id}/status",
        json={"status": "Ready"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "Ready"

    # Transition to Completed
    comp_res = client.patch(
        f"/api/orders/{order_id}/status",
        json={"status": "Completed"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == "Completed"


def test_order_filter_by_status(client, admin_token):
    res = client.get("/api/orders?status=Pending", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    orders = res.json()
    for o in orders:
        assert o["status"] == "Pending"


def test_admin_summary_metrics(client, admin_token):
    summary_res = client.get("/api/admin/summary", headers={"Authorization": f"Bearer {admin_token}"})
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert "pending_orders" in summary
    assert "preparing_orders" in summary
    assert "ready_orders" in summary
    assert "completed_orders" in summary
    assert "total_orders" in summary
    assert "available_menu_items" in summary
    assert "unavailable_menu_items" in summary


def test_unauthenticated_orders_access_fails(client):
    res = client.get("/api/orders")
    assert res.status_code == 401
