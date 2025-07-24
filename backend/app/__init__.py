from flask import Flask
from flask_restful import Api
from app.api.device_data import DeviceData
from app.api.range import TimeRange
from app.api.device_latest import DeviceLatest
from app.api.comparison import Comparison

def create_app():
    app = Flask(__name__)
    api = Api(app)

    # register routes
    api.add_resource(DeviceData, "/api/devices/<int:device_id>/data")
    api.add_resource(TimeRange, "/api/devices/range")
    api.add_resource(DeviceLatest, "/api/devices/<int:device_id>/latest")
    api.add_resource(Comparison, "/api/comparison")

    return app
