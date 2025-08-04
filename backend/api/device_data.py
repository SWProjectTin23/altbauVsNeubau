from flask_restful import Resource
from flask import request, jsonify
import psycopg2 # Import psycopg2 for database operations

# Import database operation functions
from db_operations import get_device_data_from_db, device_exists

class DeviceData(Resource):
    def get(self, device_id):
        try:
            # Returns all available data for the specified device
            start = request.args.get("start", type=int)
            end = request.args.get("end", type=int)

            # Validate that the device ID is provided
            if not device_exists(device_id):
                return {
                    "status": "error",
                    "message": f"Device with ID {device_id} does not exist."
                }, 404
            
            # Get data from the database
            data = get_device_data_from_db(device_id, start=start, end=end)

            # If no data is found, return an empty list with a success status
            if not data:
                return {
                    "device_id": device_id,
                    "start": start,
                    "end": end,
                    "status": "success",
                    "data": [],
                    "message": f"No data available for device {device_id} in the specified range."
                }, 200
            
            # Return the data in JSON format
            return {
                "device_id": device_id,
                "start": start,
                "end": end,
                "status": "success",
                "data": data,
                "message": None
            }, 200
        
        except psycopg2.Error as e:
            print(f"Database error in DeviceData: {e}")
            return {
                "status": "error",
                "message": "A database error occurred while processing your request."
            }, 500
        
        except ValueError as ve:
            print(f"Value error in DeviceData: {ve}")
            return {
                "status": "error",
                "message": str(ve)
            }, 400
        
        except Exception as e:
            print(f"An unexpected error occurred in DeviceData: {e}")
            return {
                "status": "error",
                "message": "An unexpected error occurred."
            }, 500