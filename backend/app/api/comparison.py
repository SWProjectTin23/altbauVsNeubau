from flask_restful import Resource
from flask import request, jsonify
import psycopg2
from .database.db_operations import get_device_data_from_db, device_exists


class Comparison(Resource):
    def get(self):
        try:
            # Extract query parameters
            device_1 = request.args.get("device_1", type=int)
            device_2 = request.args.get("device_2", type=int)
            metric = request.args.get("metric")
            start = request.args.get("start", type=int)
            end = request.args.get("end", type=int)

            # Validate required parameters
            if metric not in ["temperature", "humidity", "pollen", "particulate_matter"]:
                return {"error": "Invalid metric"}, 400

            if not device_exists(device_1):
                return {"error": f"Device {device_1} not found."}, 404
            if not device_exists(device_2):
                return {"error": f"Device {device_2} not found."}, 404

            # get data for device 1
            data_device_1 = get_device_data_from_db(device_1, metric, start, end)
            
            # get data for device 2
            data_device_2 = get_device_data_from_db(device_2, metric, start, end)
            


            # Return the comparison data
            return jsonify({
                f"device_{device_1}": data_device_1,
                f"device_{device_2}": data_device_2
            })
        
        # Handle database connection errors
        except psycopg2.Error as e:
            return {"error": f"Database error: {str(e)}"}, 500
        
        # Handle other exceptions
        except Exception as e:
            return {"error": str(e)}, 400
