from flask_restful import Resource
from psycopg2 import Error as PsycopgError

# logging
from common.logging_setup import setup_logger, log_event, DurationTimer

# unified app exceptions (no direct psycopg2 usage here)
from common.exceptions import (
    DatabaseError,
    DatabaseQueryTimeoutError,
    DatabaseOperationalError,
    AppError,
)

# db ops
from .db_operations import get_all_device_time_ranges_from_db

# each module registers its own logger
logger = setup_logger(service="api", module="range")


class TimeRange(Resource):
    def get(self):
        timer = DurationTimer().start()
        log_event(logger, "INFO", "time_range.start")

        try:
            # Returns the earliest and latest timestamps for each device
            time_ranges = get_all_device_time_ranges_from_db()

            # If no time ranges are found, return an empty list with a success status
            if not time_ranges:
                log_event(logger, "INFO", "time_range.empty", duration_ms=timer.stop_ms())
                return {
                    "status": "success",
                    "message": "No time ranges found for any devices.",
                    "data": []
                }, 200

            log_event(
                logger, "INFO", "time_range.ok",
                duration_ms=timer.stop_ms(), device_count=len(time_ranges)
            )
            return {
                "status": "success",
                "data": time_ranges
            }, 200

        # --- mapped DB failures (unified, no psycopg2 leak) ---
        except DatabaseQueryTimeoutError as e:
            log_event(
                logger, "ERROR", "time_range.db_query_timeout",
                duration_ms=timer.stop_ms(), **e.to_log_fields()
            )
            return {
                "status": "error",
                "message": "database query timeout"
            }, 504

        except DatabaseOperationalError as e:
            log_event(
                logger, "ERROR", "time_range.db_operational_error",
                duration_ms=timer.stop_ms(), **e.to_log_fields()
            )
            return {
                "status": "error",
                "message": "database temporarily unavailable"
            }, 503

        except DatabaseError as e:
            log_event(
                logger, "ERROR", "time_range.db_error",
                duration_ms=timer.stop_ms(), **e.to_log_fields()
            )
            return {
                "status": "error",
                "message": "database error"
            }, 500

        except PsycopgError as e:
            log_event(logger, "ERROR", "range.db_psycopg2_error",
                      duration_ms=timer.stop_ms())
            return {"status": "error", "message": "A database error occurred while processing your request."}, 500

        # generic app-level errors (if any bubbled up)
        except AppError as e:
            log_event(
                logger, "ERROR", "time_range.app_error",
                duration_ms=timer.stop_ms(), **e.to_log_fields()
            )
            return {
                "status": "error",
                "message": e.message
            }, 500

        # unexpected
        except Exception as e:
            log_event(
                logger, "ERROR", "time_range.unhandled_exception",
                duration_ms=timer.stop_ms(),
                error_type=e.__class__.__name__, error_msg=str(e)[:200]
            )
            return {
                "status": "error",
                "message": "An unexpected error occurred."
            }, 400
