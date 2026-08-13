"""Product listing and management endpoints."""

from flask import Blueprint, current_app, jsonify, request

from app.auth import get_current_user_id
from app.extensions import db, redis_client
from app.models import Product

bp = Blueprint("products", __name__, url_prefix="/api/products")


def _hot_cache_key(category_id):
    return f"products:hot:{category_id}"


def _serialize_products(products):
    return [product.to_dict() for product in products]


@bp.get("")
def list_products():
    """Paginated product list with optional category filter and cache."""
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)
    category_id = request.args.get("category_id", type=int)

    # The hottest read path is the first page of an entire category.
    if page == 1 and category_id is not None:
        cache_key = _hot_cache_key(category_id)
        cached = redis_client.get_json(cache_key)
        if cached is not None:
            return jsonify({"code": 0, "data": cached, "source": "cache"})

    query = Product.query.filter_by(status=Product.STATUS_ON_SALE)
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )
    result = {
        "items": _serialize_products(pagination.items),
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }

    if page == 1 and category_id is not None:
        redis_client.set_json(
            _hot_cache_key(category_id),
            result,
            current_app.config["PRODUCT_CACHE_TTL"],
        )

    return jsonify({"code": 0, "data": result, "source": "db"})


@bp.get("/<int:product_id>")
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"code": 404, "message": "product not found"}), 404
    return jsonify({"code": 0, "data": product.to_dict()})


@bp.post("")
def create_product():
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"code": 401, "message": "authentication required"}), 401

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    price = data.get("price")
    if not title or not isinstance(price, (int, float)) or price <= 0:
        return jsonify({"code": 400, "message": "invalid title or price"}), 400

    product = Product(
        seller_id=user_id,
        category_id=int(data.get("category_id") or 0),
        title=title,
        description=data.get("description") or "",
        price=price,
        images=data.get("images") or [],
    )
    db.session.add(product)
    db.session.commit()

    redis_client.delete_pattern(
        _hot_cache_key(product.category_id) + "*"
    )

    return jsonify({"code": 0, "data": product.to_dict()}), 201

