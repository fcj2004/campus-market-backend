"""Development server entry point.

This script will attempt to create missing database tables on startup
when running in development to make local setup easier.
"""

from app import create_app
from app.extensions import db

app = create_app()


def _ensure_tables():
    try:
        with app.app_context():
            print('Creating tables on DB:', app.config.get('SQLALCHEMY_DATABASE_URI'))
            db.create_all()
            try:
                # Import and run the seed script to populate demo data in dev.
                from scripts import seed_data

                seed_data.seed()
            except Exception:
                # Don't fail startup if seeding fails.
                pass
    except Exception:
        # Ignore errors here; app will raise them again on use. This
        # keeps development startup resilient when optional services
        # (like remote MySQL) are unavailable.
        pass


if __name__ == "__main__":
    _ensure_tables()
    app.run(host="0.0.0.0", port=5000, debug=True)

