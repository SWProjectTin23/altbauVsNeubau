from flask_restful import Resource
from flask import jsonify
import psycopg2 # Import psycopg2 for specific error handling

# Import the new database function
from .database.db_operations import get_all_device_time_ranges_from_db

class TimeRange(Resource):
    def get(self):
        try:
            # Fetch all device time ranges from the database
            time_ranges = get_all_device_time_ranges_from_db()
            
            # If no data is found in the database, return an empty object or an error
            if not time_ranges:
                return jsonify({"message": "No device data found in the database."}), 200 # Or 404 if no devices at all
            
            return jsonify(time_ranges)

        except psycopg2.Error as e:
            # Catch specific PostgreSQL errors.
            print(f"A database error occurred in TimeRange: {e}")
            return {"error": "An internal database error occurred. Please try again later."}, 500
        except Exception as e:
            # Catch all other unexpected errors.
            print(f"An unexpected error occurred in TimeRange: {e}")
            return {"error": "An unexpected error occurred."}, 400