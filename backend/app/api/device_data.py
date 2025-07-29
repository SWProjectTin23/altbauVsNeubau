from flask_restful import Resource
from flask import request, jsonify
import psycopg2 # Import psycopg2 for database operations

# Import database operation functions
from .database.db_operations import get_device_data_from_db, device_exists

class DeviceData(Resource):
    def get(self, device_id):
        try:
            # Returns all available data for the specified device
            start = request.args.get("start", type=str)
            end = request.args.get("end", type=str)

            if not device_exists(device_id):
                return {"error": f"Device {device_id} not found."}, 404
            
            # Fetch data from the database
            data = get_device_data_from_db(device_id, start=start, end=end)

            # If no data is found, return a 404 error
            if not data:
                return {"error": f"No data available for device {device_id}"}, 404

            # Return the data as JSON
            response = jsonify(data)
            response.status_code = 200
            return response

        # Handle specific database errors
        except psycopg2.Error as e:
            print(f"A database error occurred in DeviceData: {e}")
            return {"error": "A database error occurred. Please try again later."}, 500
        
        # Handle data validation errors
        except ValueError as ve:
            print(f"Value error: {ve}")
            return {"error": str(ve)}, 400

        # Handle other unexpected errors
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"error": "An unexpected error occurred."}, 400