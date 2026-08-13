"""In-app message endpoints."""

from flask import Blueprint, jsonify, request

from app.auth import get_current_user_id
from app.extensions import db
from app.models import Message

bp = Blueprint("messages", __name__, url_prefix="/api/messages")


@bp.get("")
def list_messages():
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"code": 401, "message": "authentication required"}), 401

    unread_only = request.args.get("unread_only", "0") == "1"
    query = Message.query.filter_by(receiver_id=user_id)
    if unread_only:
        query = query.filter_by(is_read=0)

    messages = query.order_by(Message.created_at.desc()).limit(100).all()
    return jsonify({"code": 0, "data": [msg.to_dict() for msg in messages]})


@bp.post("/<int:message_id>/read")
def mark_read(message_id):
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"code": 401, "message": "authentication required"}), 401

    message = db.session.get(Message, message_id)
    if not message or message.receiver_id != user_id:
        return jsonify({"code": 404, "message": "message not found"}), 404

    message.is_read = 1
    db.session.commit()
    return jsonify({"code": 0, "data": message.to_dict()})

