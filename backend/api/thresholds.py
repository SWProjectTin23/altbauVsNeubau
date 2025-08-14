from flask_restful import Resource
from flask import request

# logging
from common.logging_setup import setup_logger, log_event, DurationTimer, save_invalid_payload

# unified app exceptions
from common.exceptions import (
    DatabaseError,
    DatabaseQueryTimeoutError,
    DatabaseOperationalError,
    AppError,
)

# db ops
from .db_operations import get_thresholds_from_db, update_thresholds_in_db

# each module registers its own logger
logger = setup_logger(service="api", module="thresholds")


class Thresholds(Resource):
    def get(self):
        timer = DurationTimer().start()
        log_event(logger, "INFO", "thresholds.get.start")

        try:
            # Get the thresholds from the database
            thresholds = get_thresholds_from_db()

            # If no thresholds are found, return an empty list with a success status
            if not thresholds:
                log_event(logger, "INFO", "thresholds.get.empty", duration_ms=timer.stop_ms())
                return {
                    "status": "success",
                    "data": [],
                    "message": "No thresholds available."
                }, 200

            log_event(
                logger, "INFO", "thresholds.get.ok",
                duration_ms=timer.stop_ms(), row_count=len(thresholds)
            )
            return {
                "status": "success",
                "data": thresholds,
                "message": "Thresholds retrieved successfully."
            }, 200

        # --- mapped DB failures (unified) ---
        except DatabaseQueryTimeoutError as e:
            log_event(logger, "ERROR", "thresholds.get.db_query_timeout",
                      duration_ms=timer.stop_ms(), **e.to_log_fields())
            return {"status": "error", "message": "database query timeout"}, 504

        except DatabaseOperationalError as e:
            log_event(logger, "ERROR", "thresholds.get.db_operational_error",
                      duration_ms=timer.stop_ms(), **e.to_log_fields())
            return {"status": "error", "message": "database temporarily unavailable"}, 503

        except DatabaseError as e:
            log_event(logger, "ERROR", "thresholds.get.db_error",
                      duration_ms=timer.stop_ms(), **e.to_log_fields())
            return {"status": "error", "message": "database error"}, 500

        except AppError as e:
            log_event(logger, "ERROR", "thresholds.get.app_error",
                      duration_ms=timer.stop_ms(), **e.to_log_fields())
            return {"status": "error", "message": e.message}, 500

        except Exception as e:
            log_event(logger, "ERROR", "thresholds.get.unhandled_exception",
                      duration_ms=timer.stop_ms(),
                      error_type=e.__class__.__name__, error_msg=str(e)[:200])
            return {"status": "error", "message": "An unexpected error occurred while processing your request."}, 500

    def post(self):
        timer = DurationTimer().start()
        raw = request.get_data(cache=False)  # used if we need to persist invalid payloads
        log_event(logger, "INFO", "thresholds.post.start", payload_size=len(raw) if raw else 0)

        # expected keys and types
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

        try:
            threshold_data_raw = request.get_json(silent=True)

            # basic validity
            if not threshold_data_raw or not isinstance(threshold_data_raw, dict):
                # persist invalid payload for debugging (optional)
                path = save_invalid_payload(
                    "/var/log/app/invalid_payloads",
                    "thresholds_post_invalid",
                    raw if raw else b""
                )
                log_event(logger, "WARNING", "thresholds.post.bad_request.invalid_body",
                          file_path=path)
                return {
                    "status": "error",
                    "message": "Invalid input data. Expecting a Dictionary."
                }, 400

            # presence + type normalization (fixed bug: convert inside the loop)
            validated_threshold_data = {}
            for key, expected_type in expected_keys_and_types.items():
                if key not in threshold_data_raw:
                    log_event(logger, "WARNING", "thresholds.post.bad_request.missing_key", missing_key=key)
                    return {
                        "status": "error",
                        "message": f"Missing required key: '{key}'."
                    }, 400
                value = threshold_data_raw[key]
                if value is None:
                    log_event(logger, "WARNING", "thresholds.post.bad_request.none_value", key=key)
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
                        validated_threshold_data[key] = value  # fallback (should not happen)
                except (ValueError, TypeError):
                    log_event(logger, "WARNING", "thresholds.post.bad_request.type_mismatch",
                              key=key, value=str(value)[:50], expected=expected_type.__name__)
                    return {
                        "status": "error",
                        "message": f"Invalid value for '{key}': {value}. Expected type {expected_type.__name__}."
                    }, 400

            # semantic checks
            # min_hard < max_hard
            for min_hard_key, max_hard_key in [
                ("temperature_min_hard", "temperature_max_hard"),
                ("humidity_min_hard", "humidity_max_hard"),
                ("pollen_min_hard", "pollen_max_hard"),
                ("particulate_matter_min_hard", "particulate_matter_max_hard"),
            ]:
                if validated_threshold_data[min_hard_key] >= validated_threshold_data[max_hard_key]:
                    log_event(logger, "WARNING", "thresholds.post.bad_request.minhard_ge_maxhard",
                              min_hard=min_hard_key, max_hard=max_hard_key)
                    return {"status": "error", "message": f"'{min_hard_key}' must be less than '{max_hard_key}'."}, 400

            # min_soft < max_hard
            for min_soft_key, max_hard_key in [
                ("temperature_min_soft", "temperature_max_hard"),
                ("humidity_min_soft", "humidity_max_hard"),
                ("pollen_min_soft", "pollen_max_hard"),
                ("particulate_matter_min_soft", "particulate_matter_max_hard"),
            ]:
                if validated_threshold_data[min_soft_key] >= validated_threshold_data[max_hard_key]:
                    log_event(logger, "WARNING", "thresholds.post.bad_request.minsoft_ge_maxhard",
                              min_soft=min_soft_key, max_hard=max_hard_key)
                    return {"status": "error", "message": f"'{min_soft_key}' must be less than '{max_hard_key}'."}, 400

            # min_soft < max_soft
            for min_soft_key, max_soft_key in [
                ("temperature_min_soft", "temperature_max_soft"),
                ("humidity_min_soft", "humidity_max_soft"),
                ("pollen_min_soft", "pollen_max_soft"),
                ("particulate_matter_min_soft", "particulate_matter_max_soft"),
            ]:
                if validated_threshold_data[min_soft_key] >= validated_threshold_data[max_soft_key]:
                    log_event(logger, "WARNING", "thresholds.post.bad_request.minsoft_ge_maxsoft",
                              min_soft=min_soft_key, max_soft=max_soft_key)
                    return {"status": "error", "message": f"'{min_soft_key}' must be less than '{max_soft_key}'."}, 400

            # min_hard < min_soft
            for min_hard_key, min_soft_key in [
                ("temperature_min_hard", "temperature_min_soft"),
                ("humidity_min_hard", "humidity_min_soft"),
                ("pollen_min_hard", "pollen_min_soft"),
                ("particulate_matter_min_hard", "particulate_matter_min_soft"),
            ]:
                if validated_threshold_data[min_hard_key] >= validated_threshold_data[min_soft_key]:
                    log_event(logger, "WARNING", "thresholds.post.bad_request.minhard_ge_minsoft",
                              min_hard=min_hard_key, min_soft=min_soft_key)
                    return {"status": "error", "message": f"'{min_hard_key}' must be less than '{min_soft_key}'."}, 400

            # max_hard > max_soft
            for max_hard_key, max_soft_key in [
                ("temperature_max_hard", "temperature_max_soft"),
                ("humidity_max_hard", "humidity_max_soft"),
                ("pollen_max_hard", "pollen_max_soft"),
                ("particulate_matter_max_hard", "particulate_matter_max_soft"),
            ]:
                if validated_threshold_data[max_hard_key] <= validated_threshold_data[max_soft_key]:
                    log_event(logger, "WARNING", "thresholds.post.bad_request.maxhard_le_maxsoft",
                              max_hard=max_hard_key, max_soft=max_soft_key)
                    return {"status": "error", "message": f"'{max_hard_key}' must be greater than '{max_soft_key}'."}, 400

            # min_hard < max_soft
            for min_hard_key, max_soft_key in [
                ("temperature_min_hard", "temperature_max_soft"),
                ("humidity_min_hard", "humidity_max_soft"),
                ("pollen_min_hard", "pollen_max_soft"),
                ("particulate_matter_min_hard", "particulate_matter_max_soft"),
            ]:
                if validated_threshold_data[min_hard_key] >= validated_threshold_data[max_soft_key]:
                    log_event(logger, "WARNING", "thresholds.post.bad_request.minhard_ge_maxsoft",
                              min_hard=min_hard_key, max_soft=max_soft_key)
                    return {"status": "error", "message": f"'{min_hard_key}' must be less than '{max_soft_key}'."}, 400

            # persist
            update_thresholds_in_db(validated_threshold_data)
            log_event(logger, "INFO", "thresholds.post.ok", duration_ms=timer.stop_ms())

            return {"status": "success", "message": "Thresholds updated successfully."}, 200

        # --- mapped DB failures (unified) ---
        except DatabaseQueryTimeoutError as e:
            log_event(logger, "ERROR", "thresholds.post.db_query_timeout",
                      duration_ms=timer.stop_ms(), **e.to_log_fields())
            return {"status": "error", "message": "database query timeout"}, 504

        except DatabaseOperationalError as e:
            log_event(logger, "ERROR", "thresholds.post.db_operational_error",
                      duration_ms=timer.stop_ms(), **e.to_log_fields())
            return {"status": "error", "message": "database temporarily unavailable"}, 503

        except DatabaseError as e:
            log_event(logger, "ERROR", "thresholds.post.db_error",
                      duration_ms=timer.stop_ms(), **e.to_log_fields())
            return {"status": "error", "message": "database error"}, 500

        except AppError as e:
            log_event(logger, "ERROR", "thresholds.post.app_error",
                      duration_ms=timer.stop_ms(), **e.to_log_fields())
            return {"status": "error", "message": e.message}, 500

        except Exception as e:
            log_event(logger, "ERROR", "thresholds.post.unhandled_exception",
                      duration_ms=timer.stop_ms(),
                      error_type=e.__class__.__name__, error_msg=str(e)[:200])
            return {"status": "error", "message": "An unexpected error occurred while processing your request."}, 500
