import pytest


def test_upi_payment_flow_gpay(client):
    # 1. Login as student
    login_res = client.post("/api/auth/login", json={"email": "student@example.com", "password": "prototype-password"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get menu items to pick one
    menu_res = client.get("/api/menu")
    assert menu_res.status_code == 200
    items = menu_res.json()
    item_id = items[0]["id"]

    # 3. Create an order
    order_res = client.post("/api/orders", json={"items": [{"menu_item_id": item_id, "quantity": 2}]}, headers=headers)
    assert order_res.status_code == 201
    order_data = order_res.json()
    order_id = order_data["id"]
    assert order_data["payment_status"] == "UNPAID"
    assert order_data["token_code"] is None

    # 4. Pay using Google Pay UPI ID
    pay_res = client.post(
        f"/api/orders/{order_id}/payment",
        json={"payment_method": "UPI", "upi_id": "student@okhdfcbank", "upi_app": "Google Pay"},
        headers=headers,
    )
    assert pay_res.status_code == 200
    pay_data = pay_res.json()
    assert pay_data["status"] == "SUCCESS"
    assert pay_data["transaction_reference"].startswith("UPI-TXN-")
    assert pay_data["token_code"].startswith("CANT-")

    # 5. Fetch order again and verify payment_status and token_code
    fetch_res = client.get("/api/orders", headers=headers)
    assert fetch_res.status_code == 200
    orders = fetch_res.json()
    matching = [o for o in orders if o["id"] == order_id]
    assert len(matching) == 1
    assert matching[0]["payment_status"] == "SUCCESS"
    assert matching[0]["token_code"] == pay_data["token_code"]


def test_upi_payment_flow_phonepe(client):
    # 1. Login as student
    login_res = client.post("/api/auth/login", json={"email": "student@example.com", "password": "prototype-password"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Pick item and create order
    menu_res = client.get("/api/menu")
    item_id = menu_res.json()[0]["id"]
    order_res = client.post("/api/orders", json={"items": [{"menu_item_id": item_id, "quantity": 1}]}, headers=headers)
    order_id = order_res.json()["id"]

    # 3. Pay using PhonePe UPI ID
    pay_res = client.post(
        f"/api/orders/{order_id}/payment",
        json={"payment_method": "UPI", "upi_id": "user@ybl", "upi_app": "PhonePe"},
        headers=headers,
    )
    assert pay_res.status_code == 200
    assert pay_res.json()["status"] == "SUCCESS"
    assert pay_res.json()["token_code"] is not None


def test_upi_payment_failure_and_retry(client):
    login_res = client.post("/api/auth/login", json={"email": "student@example.com", "password": "prototype-password"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    menu_res = client.get("/api/menu")
    item_id = menu_res.json()[0]["id"]
    order_res = client.post("/api/orders", json={"items": [{"menu_item_id": item_id, "quantity": 1}]}, headers=headers)
    order_id = order_res.json()["id"]

    # 1. Payment failure simulation with fail@upi
    fail_res = client.post(
        f"/api/orders/{order_id}/payment",
        json={"payment_method": "UPI", "upi_id": "fail@upi"},
        headers=headers,
    )
    assert fail_res.status_code == 200
    assert fail_res.json()["status"] == "FAILED"
    assert fail_res.json()["token_code"] is None

    # 2. Retry with successful PhonePe ID
    retry_res = client.post(
        f"/api/orders/{order_id}/payment",
        json={"payment_method": "UPI", "upi_id": "success@ybl", "upi_app": "PhonePe"},
        headers=headers,
    )
    assert retry_res.status_code == 200
    assert retry_res.json()["status"] == "SUCCESS"
    assert retry_res.json()["token_code"] is not None

    # 3. Paying again should raise 409 already paid
    dup_res = client.post(
        f"/api/orders/{order_id}/payment",
        json={"payment_method": "UPI", "upi_id": "again@ybl"},
        headers=headers,
    )
    assert dup_res.status_code == 409
