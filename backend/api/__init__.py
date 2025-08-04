from flask import Flask
from flask_restful import Api
from flask import jsonify
from flask_cors import CORS
import datetime
from api.device_data import DeviceData
from api.range import TimeRange
from api.device_latest import DeviceLatest
from api.comparison import Comparison
from api.thresholds import Thresholds  # Assuming you have a Thresholds resource defined

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:3000"])
    api = Api(app)

    # register routes
    api.add_resource(DeviceData, "/api/devices/<int:device_id>/data")
    api.add_resource(TimeRange, "/api/range")
    api.add_resource(DeviceLatest, "/api/devices/<int:device_id>/latest")
    api.add_resource(Comparison, "/api/comparison")
    api.add_resource(Thresholds, "/api/thresholds")

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