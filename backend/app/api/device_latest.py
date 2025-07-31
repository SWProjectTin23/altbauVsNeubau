from flask_restful import Resource
from flask import jsonify
from models.sensor_data import SensorData, db


class DeviceLatest(Resource):
    def get(self, device_id):
        result = db.session.query(SensorData).filter_by(device_id=device_id).order_by(SensorData.timestamp.desc()).first()
        if not result:
            return jsonify({"error": "No data found for this device"}), 404

        return {
            "device_id": result.device_id,
            "data": [
                {
                    "timestamp": str(result.timestamp.isoformat()),
                    "temperature": float(result.temperature),
                    "humidity": float(result.humidity),
                    "pollen": result.pollen,
                    "particulate_matter": result.particulate_matter
                }
            ]
        }