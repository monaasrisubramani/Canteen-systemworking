def test_public_menu_access(client):
    response = client.get("/api/menu")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_add_menu_item_success(client, admin_token):
    item_payload = {
        "name": "Paneer Tikka Roll",
        "description": "Succulent cottage cheese cubes grilled with aromatic spices wrapped in a flatbread",
        "price": 85.0,
        "category": "Snacks",
        "is_available": True,
    }
    response = client.post(
        "/api/menu",
        json=item_payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Paneer Tikka Roll"
    assert data["price"] == 85.0
    assert data["is_available"] is True
    assert "id" in data


def test_add_menu_item_validation(client, admin_token):
    # Negative price
    res_neg = client.post(
        "/api/menu",
        json={"name": "Cheap Samosa", "price": -5.0, "category": "Snacks"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_neg.status_code == 422

    # Empty name
    res_empty = client.post(
        "/api/menu",
        json={"name": "   ", "price": 20.0, "category": "Snacks"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_empty.status_code == 422


def test_add_menu_item_duplicate_rejection(client, admin_token):
    payload = {"name": "Special Pav Bhaji", "price": 70.0, "category": "Snacks"}
    res1 = client.post("/api/menu", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert res1.status_code == 201

    res2 = client.post("/api/menu", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert res2.status_code == 409


def test_admin_edit_menu_item(client, admin_token):
    # Create item
    res = client.post(
        "/api/menu",
        json={"name": "Masala Chai", "price": 15.0, "category": "Beverages"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    item_id = res.json()["id"]

    # Edit item
    edit_res = client.put(
        f"/api/menu/{item_id}",
        json={"price": 18.0, "description": "Fresh ginger and cardamom tea"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert edit_res.status_code == 200
    data = edit_res.json()
    assert data["price"] == 18.0
    assert data["description"] == "Fresh ginger and cardamom tea"
    assert data["name"] == "Masala Chai"


def test_admin_toggle_menu_item_availability(client, admin_token):
    # Create item
    res = client.post(
        "/api/menu",
        json={"name": "Mango Lassi", "price": 40.0, "category": "Beverages", "is_available": True},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    item_id = res.json()["id"]
    assert res.json()["is_available"] is True

    # Toggle to unavailable
    toggle1 = client.patch(
        f"/api/menu/{item_id}/availability",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert toggle1.status_code == 200
    assert toggle1.json()["is_available"] is False

    # Verify public menu reflects the change
    public_res = client.get(f"/api/menu/{item_id}")
    assert public_res.json()["is_available"] is False

    # Toggle back to available
    toggle2 = client.patch(
        f"/api/menu/{item_id}/availability",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert toggle2.status_code == 200
    assert toggle2.json()["is_available"] is True


def test_admin_delete_menu_item(client, admin_token):
    res = client.post(
        "/api/menu",
        json={"name": "Temporary Snack", "price": 25.0, "category": "Snacks"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    item_id = res.json()["id"]

    # Delete
    del_res = client.delete(f"/api/menu/{item_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert del_res.status_code == 200

    # Verify item is gone
    get_res = client.get(f"/api/menu/{item_id}")
    assert get_res.status_code == 404


def test_unauthenticated_menu_mutation_fails(client):
    res = client.post("/api/menu", json={"name": "Hacker Item", "price": 10.0})
    assert res.status_code == 401
