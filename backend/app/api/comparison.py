from flask_restful import Resource
from flask import request, jsonify
import psycopg2
from .database.db_operations import compare_devices_over_time, validate_timestamps_and_range

class Comparison(Resource):
    def get(self):
        try:
            # Returns the selected metric for two devices over a given time range (by default all)
            device_id1 = request.args.get("device_1", type=int)
            device_id2 = request.args.get("device_2", type=int)
            metric = request.args.get("metric")
            start = request.args.get("start")
            end = request.args.get("end")

            # Validate that a metric is specified
            if not metric:
                return {"error": "Metric must be specified."}, 400

            # Validate that both device IDs are provided
            if not device_id1 or not device_id2:
                return {"error": "Both device IDs must be provided."}, 400

            # Validate the time range if provided
            if start or end:
                is_valid, error_msg = validate_timestamps_and_range(device_id1, device_id2, start, end)
                if not is_valid:
                    return {"error": f"Invalid time range: {error_msg}"}, 400


            response = jsonify(compare_devices_over_time(device_id1, device_id2, metric, start, end))
            response.status_code = 200
            return response

        except Exception as e:
            print(f"An unexpected error occurred in Comparison API: {e}")
            return {"error": "An unexpected error occurred while processing your request."}, 500 # 500 for unexpected errors