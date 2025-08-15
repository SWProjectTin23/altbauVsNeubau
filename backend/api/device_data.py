from flask_restful import Resource
from flask import request
from psycopg2 import Error as PsycopgError
# logging
from common.logging_setup import setup_logger, log_event, DurationTimer

# unified app exceptions
from common.exceptions import (
    DatabaseError,
    DatabaseQueryTimeoutError,
    DatabaseOperationalError,
    AppError,
)

# db ops
from .db_operations import get_device_data_from_db, device_exists

# each module registers its own logger
logger = setup_logger(service="api", module="device_data")


class DeviceData(Resource):
    def get(self, device_id: int):
        timer = DurationTimer().start()

        # optional parameters
        start = request.args.get("start", type=int)
        end = request.args.get("end", type=int)
        metric = request.args.get("metric")  # optional; if absent behaves as before

        log_event(
            logger, "INFO", "device_data.start",
            device_id=device_id, start=start, end=end, metric=metric or "ALL"
        )

        # basic input guard (optional, keeps previous behavior)
        if device_id <= 0:
            log_event(logger, "WARNING", "device_data.invalid_id", device_id=device_id)
            return {
                "status": "error",
                "message": "device_id must be a positive integer."
            }, 400

        try:
            # existence check
            if not device_exists(device_id):
                log_event(logger, "WARNING", "device_data.not_found", device_id=device_id)
                return {
                    "status": "error",
                    "message": f"Device with ID {device_id} does not exist."
                }, 404

            # fetch data (passes metric if provided; backward compatible)
            data = get_device_data_from_db(device_id, metric=metric, start=start, end=end)

            # If no data is found, return an empty list with a success status
            if not data:
                log_event(
                    logger, "INFO", "device_data.empty",
                    device_id=device_id, start=start, end=end, metric=metric or "ALL",
                    duration_ms=timer.stop_ms()
                )
                return {
                    "device_id": device_id,
                    "start": start,
                    "end": end,
                    "status": "success",
                    "data": [],
                    "message": f"No data available for device {device_id} in the specified range."
                }, 200

            log_event(
                logger, "INFO", "device_data.ok",
                device_id=device_id, start=start, end=end, metric=metric or "ALL",
                row_count=len(data), duration_ms=timer.stop_ms()
            )
            return {
                "device_id": device_id,
                "start": start,
                "end": end,
                "status": "success",
                "data": data,
                "message": None
            }, 200

        # --- mapped DB failures (unified, no psycopg2 leak) ---
        except DatabaseQueryTimeoutError as e:
            log_event(
                logger, "ERROR", "device_data.db_query_timeout",
                device_id=device_id, start=start, end=end, metric=metric or "ALL",
                duration_ms=timer.stop_ms(), **e.to_log_fields()
            )
            return {
                "status": "error",
                "message": "database query timeout"
            }, 504

        except DatabaseOperationalError as e:
            log_event(
                logger, "ERROR", "device_data.db_operational_error",
                device_id=device_id, start=start, end=end, metric=metric or "ALL",
                duration_ms=timer.stop_ms(), **e.to_log_fields()
            )
            return {
                "status": "error",
                "message": "database temporarily unavailable"
            }, 503
        except DatabaseError as e:
            log_event(
                logger, "ERROR", "device_data.db_error",
                device_id=device_id, start=start, end=end, metric=metric or "ALL",
                duration_ms=timer.stop_ms(), **e.to_log_fields()
            )
            return {
                "status": "error",
                "message": "A database error occurred while processing your request."
            }, 500
        except PsycopgError as e:
            log_event(logger, "ERROR", "device_data.db_psycopg2_error",
                    duration_ms=timer.stop_ms(), error_type=e.__class__.__name__)
            return {"status": "error", "message": "A database error occurred while processing your request."}, 500
     
        # app-layer errors (if bubbled up)
        except AppError as e:
            log_event(
                logger, "ERROR", "device_data.app_error",
                device_id=device_id, start=start, end=end, metric=metric or "ALL",
                duration_ms=timer.stop_ms(), **e.to_log_fields()
            )
            return {
                "status": "error",
                "message": e.message
            }, 500

        # validation errors from inner layers (e.g., invalid metric)
        except ValueError as e:
            log_event(
                logger, "WARNING", "device_data.bad_request",
                device_id=device_id, start=start, end=end, metric=metric or "ALL",
                error_msg=str(e), duration_ms=timer.stop_ms()
            )
            return {
                "status": "error",
                "message": str(e)
            }, 400

        # unexpected
        except Exception as e:
            log_event(
                logger, "ERROR", "device_data.unhandled_exception",
                device_id=device_id, start=start, end=end, metric=metric or "ALL",
                error_type=e.__class__.__name__, error_msg=str(e)[:200],
                duration_ms=timer.stop_ms()
            )
            return {
                "status": "error",
                "message": "An unexpected error occurred."
            }, 500
