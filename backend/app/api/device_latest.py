from flask_restful import Resource
from flask import jsonify
import psycopg2 # Import psycopg2 for specific error handling

# Import database operation functions
from .database.db_operations import get_device_data_from_db, device_exists

class DeviceLatest(Resource):
    def get(self, device_id):
        try:
            # Validate that the device exists
            if not device_exists(device_id):
                return {"error": f"Device {device_id} not found."}, 404

            # Get the latest data entry for the specified device
            latest_data = get_device_data_from_db(device_id)

            if latest_data is None:
                # If no data is found, return a 404 error
                return jsonify({"error": f"No data is available for device {device_id}"}), 404

            return jsonify(latest_data)

        # Catch specific PostgreSQL errors.
        except psycopg2.Error as e:
            print(f"A database error occurred in DeviceLatest: {e}")
            return {"error": "A database error occurred. Please try again later."}, 500

        # Catch all other unexpected errors.
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"error": "An unexpected error occurred."}, 400