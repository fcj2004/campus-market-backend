"""Generate demo users and products for local exploration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.extensions import db
from app.models import Product, User


def seed():
    app = create_app()
    with app.app_context():
        if User.query.count() > 0:
            print("Database already contains users; skipping seed.")
            return

        demo_users = [
            User(username="student_a", nickname="Student A"),
            User(username="student_b", nickname="Student B"),
            User(username="student_c", nickname="Student C"),
        ]
        for user in demo_users:
            user.set_password("demo123456")
        db.session.add_all(demo_users)
        db.session.flush()

        products = [
            Product(
                seller_id=demo_users[0].id,
                category_id=1,
                title="Data Structures Textbook",
                description="Nearly new, no highlights.",
                price=25.5,
                images=[],
            ),
            Product(
                seller_id=demo_users[0].id,
                category_id=1,
                title="Mechanical Keyboard",
                description="Cherry MX Brown, lightly used.",
                price=180,
                images=[],
            ),
            Product(
                seller_id=demo_users[1].id,
                category_id=2,
                title="Electric Scooter",
                description="36V, 25km range, helmet included.",
                price=620,
                images=[],
            ),
            Product(
                seller_id=demo_users[2].id,
                category_id=3,
                title="Dorm Mini Fridge",
                description="48L, energy saving, quiet.",
                price=260,
                images=[],
            ),
        ]
        db.session.add_all(products)
        db.session.commit()
        print("Seeded 3 demo users and 4 products.")


if __name__ == "__main__":
    seed()

