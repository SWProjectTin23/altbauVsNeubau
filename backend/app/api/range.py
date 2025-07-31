from flask_restful import Resource
from flask import jsonify
from sqlalchemy import func
from models.sensor_data import SensorData, db


class TimeRange(Resource):
    def get(self):
        results = db.session.query(
            SensorData.device_id,
            func.min(SensorData.timestamp),
            func.max(SensorData.timestamp)
        ).group_by(SensorData.device_id).order_by(SensorData.device_id.asc()).all()

        response = []
        for device_id, start_time, end_time in results:
            response.append({
                f"Device ID {device_id}": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                }
            })
        
        return jsonify(response)