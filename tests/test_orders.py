"""Order endpoint tests."""


def _create_product(client, headers):
    return client.post(
        "/api/products",
        headers=headers,
        json={
            "title": "Used Laptop",
            "description": "Good condition",
            "price": 1200,
            "category_id": 2,
            "images": [],
        },
    ).get_json()["data"]


def test_create_order_success(client, auth_headers):
    seller = auth_headers["alice"]
    buyer = auth_headers["bob"]
    product = _create_product(client, seller["headers"])

    response = client.post(
        "/api/orders",
        headers=buyer["headers"],
        json={"product_id": product["id"]},
    )
    assert response.status_code == 201
    order = response.get_json()["data"]
    assert order["buyer_id"] == buyer["user_id"]
    assert order["seller_id"] == seller["user_id"]
    assert order["amount"] == 1200

    # Product should be marked as sold.
    product_detail = client.get(f"/api/products/{product['id']}").get_json()["data"]
    assert product_detail["status"] == 2


def test_create_order_for_own_product_rejected(client, auth_headers):
    alice = auth_headers["alice"]
    product = _create_product(client, alice["headers"])

    response = client.post(
        "/api/orders",
        headers=alice["headers"],
        json={"product_id": product["id"]},
    )
    assert response.status_code == 400


def test_list_orders_by_role(client, auth_headers):
    seller = auth_headers["alice"]
    buyer = auth_headers["bob"]
    product = _create_product(client, seller["headers"])
    client.post(
        "/api/orders",
        headers=buyer["headers"],
        json={"product_id": product["id"]},
    )

    buyer_orders = client.get(
        "/api/orders?role=buyer",
        headers=buyer["headers"],
    ).get_json()["data"]
    seller_orders = client.get(
        "/api/orders?role=seller",
        headers=seller["headers"],
    ).get_json()["data"]

    assert buyer_orders["total"] == 1
    assert seller_orders["total"] == 1
    assert buyer_orders["items"][0]["buyer_id"] == buyer["user_id"]
    assert seller_orders["items"][0]["seller_id"] == seller["user_id"]

