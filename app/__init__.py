"""Application factory."""

from flask import Flask, jsonify

from config import Config
from app.extensions import db, redis_client


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    redis_client.init_app(app)

    register_blueprints(app)
    register_error_handlers(app)

    return app


def register_blueprints(app):
    """Register all API blueprints."""
    from app.auth import bp as auth_bp
    from app.products import bp as products_bp
    from app.orders import bp as orders_bp
    from app.messages import bp as messages_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(messages_bp)


def register_error_handlers(app):
    """Register consistent JSON error responses."""

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"code": 404, "message": "resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"code": 500, "message": "internal server error"}), 500

