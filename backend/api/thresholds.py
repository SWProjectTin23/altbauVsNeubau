from flask_restful import Resource
from flask import jsonify, request
import psycopg2  # keep: tests expect us to catch psycopg2.Error

# optional structured logging (doesn't change responses)
from common.logging_setup import setup_logger, log_event, DurationTimer

# db ops
from api.db import get_thresholds_from_db, update_thresholds_in_db

logger = setup_logger(service="api", module="thresholds")


class Thresholds(Resource):
    def get(self):
        t = DurationTimer().start()
        log_event(logger, "INFO", "thresholds.get.start")
        try:
            thresholds = get_thresholds_from_db()

            if not thresholds:
                log_event(logger, "INFO", "thresholds.get.empty", duration_ms=t.stop_ms())
                return {
                    "status": "success",
                    "data": [],
                    "message": "No thresholds available."
                }, 200

            log_event(logger, "INFO", "thresholds.get.ok", row_count=len(thresholds), duration_ms=t.stop_ms())
            return {
                "status": "success",
                "data": thresholds,
                "message": "Thresholds retrieved successfully."
            }, 200

        except psycopg2.Error as e:
            # keep original behavior & message for tests
            print(f"Database error in Thresholds: {e}")
            log_event(logger, "ERROR", "thresholds.get.db_error", error_type=e.__class__.__name__, duration_ms=t.stop_ms())
            return {
                "status": "error",
                "message": "A database error occurred while processing your request."
            }, 500

        except Exception as e:
            print(f"An unexpected error occurred in Thresholds API: {e}")
            log_event(logger, "ERROR", "thresholds.get.unhandled_exception",
                      error_type=e.__class__.__name__, error_msg=str(e)[:200], duration_ms=t.stop_ms())
            return {
                "status": "error",
                "message": "An unexpected error occurred while processing your request."
            }, 500

    def post(self):
        t = DurationTimer().start()
        log_event(logger, "INFO", "thresholds.post.start")

        try:
            threshold_data_raw = request.get_json()

            # keep original response text
            if not threshold_data_raw or not isinstance(threshold_data_raw, dict):
                log_event(logger, "WARNING", "thresholds.post.invalid_body", duration_ms=t.stop_ms())
                return {
                    "status": "error",
                    "message": "Invalid input data. Expecting a Dictionary."
                }, 400

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
            # FIX: perform casting **inside** the loop (bug in original code)
            for key, expected_type in expected_keys_and_types.items():
                if key not in threshold_data_raw:
                    log_event(logger, "WARNING", "thresholds.post.missing_key", missing_key=key)
                    return {
                        "status": "error",
                        "message": f"Missing required key: '{key}'."
                    }, 400

                value = threshold_data_raw[key]
                if value is None:
                    log_event(logger, "WARNING", "thresholds.post.none_value", key=key)
                    return {
                        "status": "error",
                        "message": f"Value for '{key}' cannot be None."
                    }, 400

                try:
                    if expected_type == float:
                        validated_threshold_data[key] = float(value)
                    elif expected_type == int:
                        validated_threshold_data[key] = int(value)
                    else:
                        validated_threshold_data[key] = value
                except (ValueError, TypeError):
                    log_event(logger, "WARNING", "thresholds.post.type_mismatch", key=key)
                    return {
                        "status": "error",
                        "message": f"Invalid value for '{key}': {value}. Expected type {expected_type.__name__}."
                    }, 400

            # Constraints (order preserved to match original)
            minhard_maxhard_pairs = [
                ("temperature_min_hard", "temperature_max_hard"),
                ("humidity_min_hard", "humidity_max_hard"),
                ("pollen_min_hard", "pollen_max_hard"),
                ("particulate_matter_min_hard", "particulate_matter_max_hard"),
            ]
            for min_hard_key, max_hard_key in minhard_maxhard_pairs:
                if validated_threshold_data[min_hard_key] >= validated_threshold_data[max_hard_key]:
                    log_event(logger, "WARNING", "thresholds.post.check_minhard_lt_maxhard",
                              min_hard=min_hard_key, max_hard=max_hard_key)
                    return {
                        "status": "error",
                        "message": f"'{min_hard_key}' must be less than '{max_hard_key}'."
                    }, 400

            minsoft_maxhard_pairs = [
                ("temperature_min_soft", "temperature_max_hard"),
                ("humidity_min_soft", "humidity_max_hard"),
                ("pollen_min_soft", "pollen_max_hard"),
                ("particulate_matter_min_soft", "particulate_matter_max_hard"),
            ]
            for min_soft_key, max_hard_key in minsoft_maxhard_pairs:
                if validated_threshold_data[min_soft_key] >= validated_threshold_data[max_hard_key]:
                    log_event(logger, "WARNING", "thresholds.post.check_minsoft_lt_maxhard",
                              min_soft=min_soft_key, max_hard=max_hard_key)
                    return {
                        "status": "error",
                        "message": f"'{min_soft_key}' must be less than '{max_hard_key}'."
                    }, 400

            minsoft_maxsoft_pairs = [
                ("temperature_min_soft", "temperature_max_soft"),
                ("humidity_min_soft", "humidity_max_soft"),
                ("pollen_min_soft", "pollen_max_soft"),
                ("particulate_matter_min_soft", "particulate_matter_max_soft"),
            ]
            for min_soft_key, max_soft_key in minsoft_maxsoft_pairs:
                if validated_threshold_data[min_soft_key] >= validated_threshold_data[max_soft_key]:
                    log_event(logger, "WARNING", "thresholds.post.check_minsoft_lt_maxsoft",
                              min_soft=min_soft_key, max_soft=max_soft_key)
                    return {
                        "status": "error",
                        "message": f"'{min_soft_key}' must be less than '{max_soft_key}'."
                    }, 400

            minhard_minsoft_pairs = [
                ("temperature_min_hard", "temperature_min_soft"),
                ("humidity_min_hard", "humidity_min_soft"),
                ("pollen_min_hard", "pollen_min_soft"),
                ("particulate_matter_min_hard", "particulate_matter_min_soft"),
            ]
            for min_hard_key, min_soft_key in minhard_minsoft_pairs:
                if validated_threshold_data[min_hard_key] >= validated_threshold_data[min_soft_key]:
                    log_event(logger, "WARNING", "thresholds.post.check_minhard_lt_minsoft",
                              min_hard=min_hard_key, min_soft=min_soft_key)
                    return {
                        "status": "error",
                        "message": f"'{min_hard_key}' must be less than '{min_soft_key}'."
                    }, 400

            maxhard_maxsoft_pairs = [
                ("temperature_max_hard", "temperature_max_soft"),
                ("humidity_max_hard", "humidity_max_soft"),
                ("pollen_max_hard", "pollen_max_soft"),
                ("particulate_matter_max_hard", "particulate_matter_max_soft"),
            ]
            for max_hard_key, max_soft_key in maxhard_maxsoft_pairs:
                if validated_threshold_data[max_hard_key] <= validated_threshold_data[max_soft_key]:
                    log_event(logger, "WARNING", "thresholds.post.check_maxhard_gt_maxsoft",
                              max_hard=max_hard_key, max_soft=max_soft_key)
                    return {
                        "status": "error",
                        "message": f"'{max_hard_key}' must be greater than '{max_soft_key}'."
                    }, 400

            minhard_maxsoft_pairs = [
                ("temperature_min_hard", "temperature_max_soft"),
                ("humidity_min_hard", "humidity_max_soft"),
                ("pollen_min_hard", "pollen_max_soft"),
                ("particulate_matter_min_hard", "particulate_matter_max_soft"),
            ]
            for min_hard_key, max_soft_key in minhard_maxsoft_pairs:
                if validated_threshold_data[min_hard_key] >= validated_threshold_data[max_soft_key]:
                    log_event(logger, "WARNING", "thresholds.post.check_minhard_lt_maxsoft",
                              min_hard=min_hard_key, max_soft=max_soft_key)
                    return {
                        "status": "error",
                        "message": f"'{min_hard_key}' must be less than '{max_soft_key}'."
                    }, 400

            # DB update (behavior unchanged)
            update_thresholds_in_db(validated_threshold_data)
            log_event(logger, "INFO", "thresholds.post.ok", duration_ms=t.stop_ms())
            return {
                "status": "success",
                "message": "Thresholds updated successfully."
            }, 200

        except psycopg2.Error as e:
            print(f"Database error in Thresholds POST: {e}")
            log_event(logger, "ERROR", "thresholds.post.db_error",
                      error_type=e.__class__.__name__, duration_ms=t.stop_ms())
            return {
                "status": "error",
                "message": "A database error occurred while processing your request."
            }, 500

        except Exception as e:
            print(f"An unexpected error occurred in Thresholds POST: {e}")
            log_event(logger, "ERROR", "thresholds.post.unhandled_exception",
                      error_type=e.__class__.__name__, error_msg=str(e)[:200], duration_ms=t.stop_ms())
            return {
                "status": "error",
                "message": "An unexpected error occurred while processing your request."
            }, 500
