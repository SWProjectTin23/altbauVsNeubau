from flask_restful import Resource
from flask import request, jsonify
import psycopg2
from db_operations import compare_devices_over_time, validate_timestamps_and_range

class Comparison(Resource):
    def get(self):
        try:
            # Returns the selected metric for two devices over a given time range (by default all)
            device_id1 = request.args.get("device_1", type=int)
            device_id2 = request.args.get("device_2", type=int)
            metric = request.args.get("metric")
            start = request.args.get("start", type=int)
            end = request.args.get("end", type=int)

            # Validate that the metric is specified
            if not metric:
                return {"status": "error", "message": "Metric must be specified."}, 400

            # Validate that both device IDs are provided
            if not device_id1 or not device_id2:
                return {"status": "error", "message": "Both device IDs must be provided."}, 400

            # Optional: Validate the time range if provided
            if start or end:
                is_valid, error_msg = validate_timestamps_and_range(device_id1, device_id2, start, end)
                if not is_valid:
                    return {"status": "error", "message": f"Invalid time range: {error_msg}"}, 400

            data = compare_devices_over_time(device_id1, device_id2, metric, start, end)

            # If no data is found, return an empty list
            if not data or (not data.get('device_1') and not data.get('device_2')):
                return {
                    "device_1": [],
                    "device_2": [],
                    "metric": metric,
                    "start": start,
                    "end": end,
                    "status": "success",
                    "message": "No data found for the specified devices and metric."
                }, 200

            return {
                "device_1": data.get('device_1', []),
                "device_2": data.get('device_2', []),
                "metric": metric,
                "start": start,
                "end": end,
                "status": "success",
                "message": None
            }, 200

        except Exception as e:
            print(f"An unexpected error occurred in Comparison API: {e}")
            return {"status": "error", "message": "An unexpected error occurred while processing your request."}, 500 # 500 for unexpected errors