import hmac
import threading

from flask import Flask, jsonify, request

from .models import Order, OrderValidationError
from .printer import render_order


def create_app(p, auth_token):
    app = Flask(__name__)
    print_lock = threading.Lock()

    @app.post("/orders")
    def receive_order():
        if auth_token:
            provided = request.headers.get("Authorization", "")
            expected = f"Bearer {auth_token}"
            if not hmac.compare_digest(provided, expected):
                return jsonify(error="unauthorized"), 401

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="invalid JSON body"), 400

        try:
            order = Order.from_dict(data)
        except OrderValidationError as e:
            return jsonify(error=str(e)), 400

        with print_lock:
            render_order(p, order)

        return jsonify(status="printed", order_number=order.number), 201

    return app
