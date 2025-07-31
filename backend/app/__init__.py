from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:postgres@db:5432/altbau_vs_neubau"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 初始化 SQLAlchemy
    db.init_app(app)

    from app.api.device_data import DeviceData
    from app.api.range import TimeRange
    from app.api.device_latest import DeviceLatest
    from app.api.comparison import Comparison

    api = Api(app)
    
    # register routes
    api.add_resource(DeviceData, "/api/devices/<int:device_id>/data")
    api.add_resource(TimeRange, "/api/devices/range")
    api.add_resource(DeviceLatest, "/api/devices/<int:device_id>/latest")
    api.add_resource(Comparison, "/api/comparison")

    app.route('/')
    def index():
        return "Dieser Port ist Eigentum der Gruppe 1 - AltbauVsNeubau. Jegliche Angriffe auf diesen Port werden nicht ohne Konsequenzen bleiben."

    return app
