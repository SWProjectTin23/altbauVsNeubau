from flask_restful import Resource
from flask import jsonify
import psycopg2 # Import psycopg2 for specific error handling

# Import database operation functions
from .database.db_operations import get_latest_device_data_from_db, device_exists

class DeviceLatest(Resource):
    def get(self, device_id):
        try:
            # Returns the latest data for the specified device
            if not device_exists(device_id):
                return {"error": f"Device {device_id} not found."}, 404
            data = get_latest_device_data_from_db(device_id)
            if not data:
                return {"error": f"No data available for device {device_id}"}, 404

            response = jsonify(data)
            response.status_code = 200
            return response

        except psycopg2.Error as e:
            print(f"A database error occurred in DeviceLatest: {e}")
            return {"error": "A database error occurred. Please try again later."}, 500
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"error": "An unexpected error occurred."}, 400