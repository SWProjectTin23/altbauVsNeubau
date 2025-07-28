from flask_restful import Resource
from flask import request, jsonify
import psycopg2 # Importiere psycopg2 für die spezifische Fehlerbehandlung

# Import database operation functions
from .database.db_operations import get_device_data_from_db, device_exists

class DeviceData(Resource):
    def get(self, device_id):
        try:
            # Extract query parameters
            start = request.args.get("start", type=int)
            end = request.args.get("end", type=int)

            # Validate that the device exists
            if not device_exists(device_id):
                return {"error": f"Device {device_id} not found."}, 404

            # Get all device data for the specified device
            device_data = get_device_data_from_db(device_id, start, end)

            # If no data is found, return a 404 error
            if not device_data:
                return {"error": f"No data found for device {device_id} within the specified range, or device does not exist."}, 404

            # Return the device data as JSON
            return jsonify(device_data)

        # Catch specific PostgreSQL errors.
        except psycopg2.Error as e:
            print(f"A database error occurred in DeviceData: {e}")
            return {"error": "An internal database error occurred. Please try again later."}, 500
        
        # Catch all other unexpected errors.
        except Exception as e:
            print(f"An unexpected error occurred in DeviceData: {e}")
            return {"error": "An unexpected error occurred."}, 400