from flask_restful import Resource
from flask import request, jsonify
from models.sensor_data import SensorData, db
from dateutil.parser import isoparse

class Comparison(Resource):
    def get(self):
        try:
            device_1 = request.args.get("device_1", type=int)
            device_2 = request.args.get("device_2", type=int)
            metric = request.args.get("metric")
            start_str = request.args.get("start")
            end_str = request.args.get("end")

            if metric not in ["temperature", "humidity", "pollen", "particulate_matter"]:
                return {"error": "Invalid metric"}, 400
        except Exception as e:
            return {"error": str(e)}, 400
        
        if not start_str or not end_str:
            return jsonify([])
        try:
            start = isoparse(start_str)
            end = isoparse(end_str)
        except (ValueError, TypeError):
            return {"error": "Invalid time format. Use ISO 8601."}, 400
        
            
        def fetch_metric_data(device_id, metric_name):
                metric_col = getattr(SensorData, metric_name)
                result = db.session.query(SensorData.timestamp, metric_col).filter(SensorData.device_id == device_id).filter(SensorData.timestamp >= start, SensorData.timestamp <= end).order_by(SensorData.timestamp).all()
                return [
                    {
                        "timestamp": r[0].isoformat(),
                        "value": float(r[1]) if r[1] is not None else None
                    }
                    for r in result
                ]
        
        return jsonify({
            "device_1": fetch_metric_data(device_1, metric),
            "device_2": fetch_metric_data(device_2, metric)
        })
