"""Product endpoint tests."""


def _create_product(client, headers, category_id=1):
    return client.post(
        "/api/products",
        headers=headers,
        json={
            "title": "Data Structures Textbook",
            "description": "Nearly new, no highlights",
            "price": 25.5,
            "category_id": category_id,
            "images": [],
        },
    )


def test_create_product_requires_auth(client):
    response = client.post(
        "/api/products",
        json={"title": "Book", "price": 10},
    )
    assert response.status_code == 401


def test_create_and_list_product(client, auth_headers):
    headers = auth_headers["alice"]["headers"]
    created = _create_product(client, headers)
    assert created.status_code == 201
    product_id = created.get_json()["data"]["id"]

    listed = client.get("/api/products?category_id=1")
    assert listed.status_code == 200
    data = listed.get_json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["id"] == product_id


def test_list_product_rejects_invalid_price(client, auth_headers):
    response = client.post(
        "/api/products",
        headers=auth_headers["alice"]["headers"],
        json={"title": "Bad Product", "price": -1},
    )
    assert response.status_code == 400


def test_get_product_not_found(client):
    response = client.get("/api/products/99999")
    assert response.status_code == 404

