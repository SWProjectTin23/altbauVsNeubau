from flask_restful import Resource
from flask import request, jsonify
from app.mock_data import get_mock_data

MOCK_DATA = get_mock_data()

class Comparison(Resource):
    def get(self):
        try:
            device_1 = request.args.get("device_1", type=int)
            device_2 = request.args.get("device_2", type=int)
            metric = request.args.get("metric")
            start = request.args.get("start", type=int)
            end = request.args.get("end", type=int)

            if metric not in ["temperature", "humidity", "pollen", "particulate_matter"]:
                return {"error": "Invalid metric"}, 400

            def extract_metric(device_id):
                data = MOCK_DATA.get(device_id, [])
                result = []
                for entry in data:
                    ts = entry["timestamp"]
                    if (start is None or ts >= start) and (end is None or ts <= end):
                        result.append({
                            "timestamp": ts,
                            "value": entry[metric]
                        })
                return result
            
            return jsonify({
                f"device_{device_1}": extract_metric(device_1),
                f"device_{device_2}": extract_metric(device_2)
            })

        except Exception as e:
            return {"error": str(e)}, 400
