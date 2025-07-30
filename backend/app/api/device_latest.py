from flask_restful import Resource
from flask import jsonify
import psycopg2 # Import psycopg2 for specific error handling

# Import database operation functions
from .database.db_operations import get_latest_device_data_from_db, device_exists

class DeviceLatest(Resource):
    def get(self, device_id):
        try:
            # Test if the device exists
            if not device_exists(device_id):
                return {
                    "status": "error",
                    "message": f"Device with ID {device_id} does not exist."
                }, 404
            
            # get the latest data for the device
            data = get_latest_device_data_from_db(device_id)

            # If no data is found, return an empty list with a success status
            if not data:
                return {
                    "status": "success",
                    "data": [],
                    "message": f"No data available for device {device_id}."
                }, 200
            
            # Return the data in JSON format
            return {
                "status": "success",
                "data": data,
                "message": None
            }, 200
        
        except psycopg2.Error as e:
            print(f"Database error in DeviceLatest: {e}")
            return {
                "status": "error",
                "message": "A database error occurred while processing your request."
            }, 500
        
        except ValueError as ve:
            print(f"Value error in DeviceLatest: {ve}")
            return {
                "status": "error",
                "message": str(ve)
            }, 400
        
        except Exception as e:
            print(f"An unexpected error occurred in DeviceLatest API: {e}")
            return {
                "status": "error",
                "message": "An unexpected error occurred while processing your request."
            }, 500