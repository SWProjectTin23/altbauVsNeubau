from flask_restful import Resource
from flask import request, jsonify
from models.sensor_data import SensorData, db
from dateutil.parser import isoparse

class DeviceData(Resource):
    def get(self, device_id):
        start_str = request.args.get("start")
        end_str = request.args.get("end")

        # if lack start or end time, then return data:0
        # todo: use the normal data format
        if not start_str or not end_str:
            return jsonify([])
        try:
            start = isoparse(start_str)
            end = isoparse(end_str)
        except (ValueError, TypeError):
            return {"error": "Invalid time format. Use ISO 8601."}, 400
        
        try:
            query = db.session.query(SensorData).filter(SensorData.device_id == device_id)
            query = query.filter(SensorData.timestamp >= start, SensorData.timestamp <= end)
            data = query.order_by(SensorData.timestamp).all()
        except Exception:
            return jsonify([])

        if not data:
            return jsonify([])

        return jsonify({
            "device_id": device_id,
            "data": [
                {
                    "timestamp": d.timestamp.isoformat(),
                    "temperature": float(d.temperature) if d.temperature is not None else None,
                    "humidity": float(d.humidity) if d.humidity is not None else None,
                    "pollen": d.pollen,
                    "particulate_matter": d.particulate_matter
                }
                for d in data
            ]
        })