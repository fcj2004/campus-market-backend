"""Order creation and query endpoints."""

from flask import Blueprint, jsonify, request

from app.auth import get_current_user_id
from app.extensions import db
from app.models import Message, Order, Product

bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@bp.post("")
def create_order():
    buyer_id = get_current_user_id()
    if buyer_id is None:
        return jsonify({"code": 401, "message": "authentication required"}), 401

    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    product = db.session.get(Product, product_id)
    if not product or product.status != Product.STATUS_ON_SALE:
        return jsonify({"code": 400, "message": "product unavailable"}), 400
    if product.seller_id == buyer_id:
        return jsonify({"code": 400, "message": "cannot buy own product"}), 400

    order = Order(
        buyer_id=buyer_id,
        seller_id=product.seller_id,
        product_id=product.id,
        amount=product.price,
        status=Order.STATUS_PENDING,
    )
    product.status = Product.STATUS_SOLD
    db.session.add(order)
    db.session.add(
        Message(
            sender_id=buyer_id,
            receiver_id=product.seller_id,
            product_id=product.id,
            content=f"buyer {buyer_id} created an order for your product {product.id}",
        )
    )
    db.session.commit()

    return jsonify({"code": 0, "data": order.to_dict()}), 201


@bp.get("")
def list_orders():
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"code": 401, "message": "authentication required"}), 401

    role = request.args.get("role", "buyer")
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)

    query = (
        Order.query.filter_by(buyer_id=user_id)
        if role == "buyer"
        else Order.query.filter_by(seller_id=user_id)
    )
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )
    return jsonify({
        "code": 0,
        "data": {
            "items": [order.to_dict() for order in pagination.items],
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
        },
    })

