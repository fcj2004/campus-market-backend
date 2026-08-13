"""SQLAlchemy models."""

from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

# BIGINT in MySQL, INTEGER in SQLite. SQLite only auto-increments INTEGER
# primary keys, while MySQL production tables can keep the wider type.
BigIntPK = db.BigInteger().with_variant(db.Integer(), "sqlite")


def utcnow():
    """Return current UTC as a naive datetime for database storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(BigIntPK, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(64), default="")
    avatar_url = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=utcnow)

    products = db.relationship("Product", backref="seller", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
        }


class Product(db.Model):
    __tablename__ = "products"

    STATUS_ON_SALE = 1
    STATUS_OFF_SHELF = 0
    STATUS_SOLD = 2

    id = db.Column(BigIntPK, primary_key=True, autoincrement=True)
    seller_id = db.Column(
        BigIntPK,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    images = db.Column(db.JSON)
    status = db.Column(db.SmallInteger, default=STATUS_ON_SALE)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=utcnow,
        onupdate=utcnow,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "category_id": self.category_id,
            "title": self.title,
            "description": self.description,
            "price": float(self.price),
            "images": self.images or [],
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Order(db.Model):
    __tablename__ = "orders"

    STATUS_PENDING = 1
    STATUS_COMPLETED = 2
    STATUS_CANCELLED = 3

    id = db.Column(BigIntPK, primary_key=True, autoincrement=True)
    buyer_id = db.Column(
        BigIntPK,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    seller_id = db.Column(
        BigIntPK,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id = db.Column(
        BigIntPK,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.SmallInteger, default=STATUS_PENDING)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=utcnow,
        onupdate=utcnow,
    )

    product = db.relationship("Product", backref="orders")

    def to_dict(self):
        return {
            "id": self.id,
            "buyer_id": self.buyer_id,
            "seller_id": self.seller_id,
            "product_id": self.product_id,
            "amount": float(self.amount),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(BigIntPK, primary_key=True, autoincrement=True)
    sender_id = db.Column(
        BigIntPK,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    receiver_id = db.Column(
        BigIntPK,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id = db.Column(
        BigIntPK,
        db.ForeignKey("products.id", ondelete="SET NULL"),
    )
    content = db.Column(db.String(1000), nullable=False)
    is_read = db.Column(db.SmallInteger, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "product_id": self.product_id,
            "content": self.content,
            "is_read": bool(self.is_read),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
