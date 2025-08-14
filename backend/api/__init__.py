from flask import Flask
from flask_restful import Api
from flask import jsonify
from flask_cors import CORS
import datetime
from api.thresholds import Thresholds
from api.device_data import DeviceData
from api.range import TimeRange
from api.device_latest import DeviceLatest
from api.comparison import Comparison

import uuid
from flask import g, request
from logging_configure import configure_logging
from exceptions import AppError

import logging
import os
import sys



def create_app():
    configure_logging()
    app = Flask(__name__)
    CORS(
        app,
        resources={r"/api/*": {"origins": [
            "http://217.154.215.67:3000",
            "http://localhost:3000",
            "https://hrschmllr.de",
            "http://isd-gerold.de:3000"
        ]}},
        supports_credentials=True,
        allow_headers=["*"]
    )
    api = Api(app)

    # register routes
    api.add_resource(DeviceData, "/api/devices/<int:device_id>/data")
    api.add_resource(TimeRange, "/api/range")
    api.add_resource(DeviceLatest, "/api/devices/<int:device_id>/latest")
    api.add_resource(Comparison, "/api/comparison")
    api.add_resource(Thresholds, "/api/thresholds")

    # Request-Lifecycle-Logs
    @app.before_request
    def _req_start():
        g.request_id = uuid.uuid4().hex[:12]
        app.logger.info("REQ %s START %s %s", g.request_id, request.method, request.path)

    @app.after_request
    def _req_done(resp):
        app.logger.info("REQ %s DONE %s %s", g.request_id, request.method, request.path)
        return resp

    # Central Error Handling
    @app.errorhandler(AppError)
    def handle_app_error(err: AppError):
        level = "warning" if getattr(err, "status_code", 500) < 500 else "error"
        getattr(app.logger, level)(
            "REQ %s AppError %s: %s",
            getattr(g, "request_id", "-"),
            err.__class__.__name__,
            str(err),
        )
        return jsonify({
            "status": "error",
            "error_type": err.__class__.__name__,
            "message": str(err),
        }), getattr(err, "status_code", 500)
            
    @app.errorhandler(Exception)
    def handle_unexpected(err: Exception):
        app.logger.exception("REQ %s Unhandled exception", getattr(g, "request_id", "-"))
        return jsonify({
            "status": "error",
            "error_type": "InternalServerError",
            "message": "An unexpected error occurred",
        }), 500

    # Health Endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "Service is healthy",
            "timestamp": datetime.datetime.now().isoformat()
        }), 200

    @app.route('/')
    def index():
        return "Dieser Port ist Eigentum der Gruppe 1 - AltbauVsNeubau. Jegliche Angriffe auf diesen Port werden nicht ohne Konsequenzen bleiben."

    return app
