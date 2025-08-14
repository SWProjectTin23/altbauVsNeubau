from flask_restful import Resource
from flask import jsonify
import psycopg2 # Import psycopg2 for specific error handling

# Import database operation functions
from .db_operations import get_all_device_time_ranges_from_db, device_exists

class TimeRange(Resource):
    def get(self):
        # Returns the earliest and latest timestamps for each device
        time_ranges = get_all_device_time_ranges_from_db()

        # If no time ranges are found, return an empty list with a success status
        if not time_ranges:
            return {
                "status": "success",
                "message": "No time ranges found for any devices.",
                "data": []
            }, 200

        # If time ranges are found, return them with a success status
        return {
            "status": "success",
            "data": time_ranges
        }, 200