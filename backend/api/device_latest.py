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
from api.db import get_latest_device_data_from_db, device_exists
from auth import token_required

# each module registers its own logger
logger = setup_logger(service="api", module="device_latest")


class DeviceLatest(Resource):
    method_decorators = [token_required]
    def get(self, device_id: int):
        timer = DurationTimer().start()
        log_event(logger, "INFO", "device_latest.start", device_id=device_id)

        # simple param sanity check (optional)
        if device_id <= 0:
            log_event(logger, "WARNING", "device_latest.invalid_id", device_id=device_id)
            return {
                "status": "error",
                "message": "device_id must be a positive integer."
            }, 400

        try:
            # existence check
            if not device_exists(device_id):
                log_event(logger, "WARNING", "device_latest.not_found", device_id=device_id)
                return {
                    "status": "error",
                    "message": f"Device with ID {device_id} does not exist."
                }, 404

            # fetch latest
            data = get_latest_device_data_from_db(device_id)

            # no data found is a valid success with empty payload
            if not data:
                log_event(
                    logger, "INFO", "device_latest.empty",
                    device_id=device_id, duration_ms=timer.stop_ms()
                )
                return {
                    "status": "success",
                    "data": [],
                    "message": f"No data available for device {device_id}."
                }, 200

            # success
            log_event(
                logger, "INFO", "device_latest.ok",
                device_id=device_id, duration_ms=timer.stop_ms()
            )
            return {
                "status": "success",
                "data": data,
                "message": None
            }, 200

        # --- mapped DB failures (unified, no psycopg2 leak) ---
        except DatabaseQueryTimeoutError as e:
            log_event(
                logger, "ERROR", "device_latest.db_query_timeout",
                device_id=device_id, **e.to_log_fields(), duration_ms=timer.stop_ms()
            )
            return {
                "status": "error",
                "message": "database query timeout"
            }, 504

        except DatabaseOperationalError as e:
            log_event(
                logger, "ERROR", "device_latest.db_operational_error",
                device_id=device_id, **e.to_log_fields(), duration_ms=timer.stop_ms()
            )
            return {
                "status": "error",
                "message": "database temporarily unavailable"
            }, 503

        except DatabaseError as e:
            log_event(
                logger, "ERROR", "device_latest.db_error",
                device_id=device_id, **e.to_log_fields(), duration_ms=timer.stop_ms()
            )
            return {
                "status": "error",
                "message": "database error"
            }, 500
        except PsycopgError as e:
            log_event(logger, "ERROR", "device_latest.db_psycopg2_error",
                      device_id=device_id, error_type=e.__class__.__name__,
                      duration_ms=timer.stop_ms())
            return {"status": "error", "message": "A database error occurred while processing your request."}, 500

        # generic app-level errors (if any bubbled up)
        except AppError as e:
            log_event(
                logger, "ERROR", "device_latest.app_error",
                device_id=device_id, **e.to_log_fields(), duration_ms=timer.stop_ms()
            )
            return {
                "status": "error",
                "message": e.message
            }, 500

        # validation errors surfaced as ValueError from inner layers
        except ValueError as e:
            log_event(
                logger, "WARNING", "device_latest.bad_request",
                device_id=device_id, error_msg=str(e), duration_ms=timer.stop_ms()
            )
            return {
                "status": "error",
                "message": str(e)
            }, 400

        # unexpected
        except Exception as e:
            # do not leak internals; keep log structured
            log_event(
                logger, "ERROR", "device_latest.unhandled_exception",
                device_id=device_id, error_type=e.__class__.__name__,
                error_msg=str(e)[:200], duration_ms=timer.stop_ms()
            )
            return {
                "status": "error",
                "message": "An unexpected error occurred while processing your request."
            }, 500
