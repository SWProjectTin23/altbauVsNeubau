from flask_restful import Resource
from flask import jsonify
import psycopg2 # Import psycopg2 for specific error handling

# Import database operation functions
from .database.db_operations import get_all_device_time_ranges_from_db, device_exists

class TimeRange(Resource):
    def get(self):
        try:
            # Returns the earliest and latest timestamps for each device
            time_ranges = get_all_device_time_ranges_from_db()
            response = jsonify(time_ranges)
            response.status_code = 200
            return response
        except psycopg2.Error as e:
            print(f"A database error occurred in TimeRange: {e}")
            return {"error": "A database error occurred. Please try again later."}, 500
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"error": "An unexpected error occurred."}, 400