from flask_restful import Resource
from flask import jsonify, request
import psycopg2 # Import psycopg2 for specific error handling

# Import database operation functions
from .db_operations import get_thresholds_from_db, update_thresholds_in_db

class Thresholds(Resource):
    def get(self):
        try:
            # Get the thresholds from the database
            thresholds = get_thresholds_from_db()

            # If no thresholds are found, return an empty list with a success status
            if not thresholds:
                return {
                    "status": "success",
                    "data": [],
                    "message": "No thresholds available."
                }, 200
            
            # Return the thresholds in JSON format
            return {
                "status": "success",
                "data": thresholds,
                "message": "Thresholds retrieved successfully."
            }, 200
        
        except psycopg2.Error as e:
            print(f"Database error in Thresholds: {e}")
            return {
                "status": "error",
                "message": "A database error occurred while processing your request."
            }, 500
        
        except Exception as e:
            print(f"An unexpected error occurred in Thresholds API: {e}")
            return {
                "status": "error",
                "message": "An unexpected error occurred while processing your request."
            }, 500

    def post(self):
        try:
            # Get the JSON data from the request
            threshold_data_raw = request.get_json()

            # Validate the input data
            if not threshold_data_raw or not isinstance(threshold_data_raw, dict):
                return {
                    "status": "error",
                    "message": "Invalid input data. Expecting a Dictionary."
                }, 400
            
            # Define expected keys
            expected_keys_and_types = {
                "temperature_min_soft": float, "temperature_max_soft": float,
                "temperature_min_hard": float, "temperature_max_hard": float,
                "humidity_min_soft": float, "humidity_max_soft": float,
                "humidity_min_hard": float, "humidity_max_hard": float,
                "pollen_min_soft": int, "pollen_max_soft": int,
                "pollen_min_hard": int, "pollen_max_hard": int,
                "particulate_matter_min_soft": int, "particulate_matter_max_soft": int,
                "particulate_matter_min_hard": int, "particulate_matter_max_hard": int
            }

            validated_threshold_data = {}
            for key, expected_type in expected_keys_and_types.items():
                if key not in threshold_data_raw:
                    return {
                        "status": "error",
                        "message": f"Missing required key: '{key}'."
                    }, 400
                value = threshold_data_raw[key]
                if value is None:
                    return {
                        "status": "error",
                        "message": f"Value for '{key}' cannot be None."
                    }, 400
                validated_threshold_data[key] = value

            try:
                if expected_type == float:
                    validated_threshold_data[key] = float(value)
                elif expected_type == int:
                    validated_threshold_data[key] = int(value)
                else:
                    validated_threshold_data
            except (ValueError, TypeError) as e:
                return {
                    "status": "error",
                    "message": f"Invalid value for '{key}': {value}. Expected type {expected_type.__name__}."
                }, 400
            
            # Validate that min values are less than max values
            validation_pairs = [
                ("temperature_min_soft", "temperature_max_soft"),
                ("temperature_min_hard", "temperature_max_hard"),
                ("humidity_min_soft", "humidity_max_soft"),
                ("humidity_min_hard", "humidity_max_hard"),
                ("pollen_min_soft", "pollen_max_soft"),
                ("pollen_min_hard", "pollen_max_hard"),
                ("particulate_matter_min_soft", "particulate_matter_max_soft"),
                ("particulate_matter_min_hard", "particulate_matter_max_hard")
            ]
            for min_key, max_key in validation_pairs:
                min_value = validated_threshold_data[min_key]
                max_value = validated_threshold_data[max_key]

                if min_value is not None and max_value is not None and min_value >= max_value:
                    return {
                        "status": "error",
                        "message": f"Minimum value for '{min_key}' must be less than maximum value for '{max_key}'."
                    }, 400
            
            # Validate that hard thresholds are greater than soft thresholds
            hard_soft_pairs = [
                ("temperature_min_hard", "temperature_min_soft"),
                ("temperature_max_hard", "temperature_max_soft"),
                ("humidity_min_hard", "humidity_min_soft"),
                ("humidity_max_hard", "humidity_max_soft"),
                ("pollen_min_hard", "pollen_min_soft"),
                ("pollen_max_hard", "pollen_max_soft"),
                ("particulate_matter_min_hard", "particulate_matter_min_soft"),
                ("particulate_matter_max_hard", "particulate_matter_max_soft")
            ]

            for hard_key, soft_key in hard_soft_pairs:
                hard_value = validated_threshold_data[hard_key]
                soft_value = validated_threshold_data[soft_key]

                if hard_value is not None and soft_value is not None and hard_value <= soft_value:
                    return {
                        "status": "error",
                        "message": f"Hard threshold '{hard_key}' must be greater than soft threshold '{soft_key}'."
                    }, 400
                
                        # Validate that min_hard is less than max_soft
            minhard_maxsoft_pairs = [
                ("temperature_min_hard", "temperature_max_soft"),
                ("humidity_min_hard", "humidity_max_soft"),
                ("pollen_min_hard", "pollen_max_soft"),
                ("particulate_matter_min_hard", "particulate_matter_max_soft"),
            ]

            for min_hard_key, max_soft_key in minhard_maxsoft_pairs:
                min_hard_value = validated_threshold_data[min_hard_key]
                max_soft_value = validated_threshold_data[max_soft_key]

                if min_hard_value is not None and max_soft_value is not None and min_hard_value >= max_soft_value:
                    return {
                        "status": "error",
                        "message": f"'{min_hard_key}' must be less than '{max_soft_key}'."
                    }, 400



            # Update the thresholds in the database
            update_thresholds_in_db(validated_threshold_data)

            return {
                "status": "success",
                "message": "Thresholds updated successfully."
            }, 200
       
        except psycopg2.Error as e:
            print(f"Database error in Thresholds POST: {e}")
            return {
                "status": "error",
                "message": "A database error occurred while processing your request."
            }, 500
       
        except Exception as e:
            print(f"An unexpected error occurred in Thresholds POST: {e}")
            return {
                "status": "error",
                "message": "An unexpected error occurred while processing your request."
            }, 500


            