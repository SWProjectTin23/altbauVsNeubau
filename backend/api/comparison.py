from flask_restful import Resource
from flask import request
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
from .db_operations import compare_devices_over_time, validate_timestamps_and_range

# each module registers its own logger
logger = setup_logger(service="api", module="comparison")


class Comparison(Resource):
    def get(self):
        timer = DurationTimer().start()

        # read query params
        device_id1 = request.args.get("device_1", type=int)
        device_id2 = request.args.get("device_2", type=int)
        metric = request.args.get("metric")
        start = request.args.get("start", type=int)
        end = request.args.get("end", type=int)
        num_buckets = request.args.get("buckets", type=int)

        log_event(
            logger, "INFO", "comparison.start",
            device_1=device_id1, device_2=device_id2,
            metric=metric, start=start, end=end, buckets=num_buckets
        )

        # ---- basic validations (keep messages stable) ----
        if not metric:
            log_event(logger, "WARNING", "comparison.invalid.metric_missing")
            return {"status": "error", "message": "Metric must be specified."}, 400

        if not device_id1 and not device_id2:
            log_event(logger, "WARNING", "comparison.invalid.device_ids_missing",
                      device_1=device_id1, device_2=device_id2)
            return {"status": "error", "message": "At least one device ID must be provided."}, 400

        if device_id1 is not None and device_id1 <= 0:
            log_event(logger, "WARNING", "comparison.invalid.device_id_nonpositive",
                      device_1=device_id1)
            return {"status": "error", "message": "Device ID 1 must be a positive integer."}, 400

        if device_id2 is not None and device_id2 <= 0:
            log_event(logger, "WARNING", "comparison.invalid.device_id_nonpositive",
                      device_2=device_id2)
            return {"status": "error", "message": "Device ID 2 must be a positive integer."}, 400

        # optional time range validation (only when any bound provided)
        if start is not None or end is not None:
            is_valid, error_msg = validate_timestamps_and_range(device_id1, device_id2, start, end)
            if not is_valid:
                log_event(
                    logger, "WARNING", "comparison.invalid.time_range",
                    device_1=device_id1, device_2=device_id2, start=start, end=end, reason=error_msg
                )
                return {"status": "error", "message": f"Invalid time range: {error_msg}"}, 400

        try:
            # call DB
            result = compare_devices_over_time(device_id1, device_id2, metric, start, end, num_buckets)

            data_obj = (result or {}).get("data", {})
            dev1_series = data_obj.get("device_1", []) if device_id1 else []
            dev2_series = data_obj.get("device_2", []) if device_id2 else []
            warning_msg = (result or {}).get("message")

            if not dev1_series and not dev2_series:
                log_event(
                    logger, "INFO", "comparison.empty",
                    device_1=device_id1, device_2=device_id2, metric=metric,
                    duration_ms=timer.stop_ms()
                )
                return {
                    "device_1": dev1_series,
                    "device_2": dev2_series,
                    "metric": metric,
                    "start": start,
                    "end": end,
                    "status": "success",
                    "message": "No data found for the specified devices and metric."
                }, 200

            # success
            log_event(
                logger, "INFO", "comparison.ok",
                device_1=device_id1, device_2=device_id2, metric=metric,
                rows_1=len(dev1_series), rows_2=len(dev2_series),
                warned=bool(warning_msg),
                duration_ms=timer.stop_ms()
            )
            return {
                "device_1": dev1_series,
                "device_2": dev2_series,
                "metric": metric,
                "start": start,
                "end": end,
                "status": "success",
                "message": warning_msg
            }, 200

        # ---- mapped DB failures (unified) ----
        except DatabaseQueryTimeoutError as e:
            log_event(
                logger, "ERROR", "comparison.db_query_timeout",
                device_1=device_id1, device_2=device_id2, metric=metric,
                duration_ms=timer.stop_ms(), **e.to_log_fields()
            )
            return {"status": "error", "message": "database query timeout"}, 504

        except DatabaseOperationalError as e:
            log_event(
                logger, "ERROR", "comparison.db_operational_error",
                device_1=device_id1, device_2=device_id2, metric=metric,
                duration_ms=timer.stop_ms(), **e.to_log_fields()
            )
            return {"status": "error", "message": "database temporarily unavailable"}, 503

        except DatabaseError as e:
            log_event(
                logger, "ERROR", "comparison.db_error",
                device_1=device_id1, device_2=device_id2, metric=metric,
                duration_ms=timer.stop_ms(), **e.to_log_fields()
            )
            return {"status": "error", "message": "database error"}, 500

        except PsycopgError as e:
            log_event(logger, "ERROR", "device_latest.db_psycopg2_error",
                      device_1=device_id1, device_2=device_id2, metric=metric,
                duration_ms=timer.stop_ms())
            return {"status": "error", "message": "A database error occurred while processing your request."}, 500

        # app-layer errors
        except AppError as e:
            log_event(
                logger, "ERROR", "comparison.app_error",
                device_1=device_id1, device_2=device_id2, metric=metric,
                duration_ms=timer.stop_ms(), **e.to_log_fields()
            )
            return {"status": "error", "message": e.message}, 500

        # invalid metric etc. from inner layers
        except ValueError as e:
            log_event(
                logger, "WARNING", "comparison.bad_request",
                device_1=device_id1, device_2=device_id2, metric=metric,
                error_msg=str(e), duration_ms=timer.stop_ms()
            )
            return {"status": "error", "message": str(e)}, 400

        # unexpected
        except Exception as e:
            log_event(
                logger, "ERROR", "comparison.unhandled_exception",
                device_1=device_id1, device_2=device_id2, metric=metric,
                error_type=e.__class__.__name__, error_msg=str(e)[:200],
                duration_ms=timer.stop_ms()
            )
            return {"status": "error", "message": "An unexpected error occurred while processing your request."}, 500
