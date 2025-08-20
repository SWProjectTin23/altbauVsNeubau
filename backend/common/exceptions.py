from typing import Any, Dict, Optional


class AppError(Exception):
    """
    Base class for all application-level errors (HTTP and non-HTTP).
    - No logging side effects here: logging is done by the caller.
    - For non-HTTP domains, prefer `error_code` (e.g., "DB_TIMEOUT", "MQTT_CONN_FAIL").
    - Use `details` to attach small, safe, non-PII context (kept minimal).
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_log_fields(self) -> Dict[str, Any]:
        """
        Return structured fields for logging (safe to put into JSON logs).
        """
        fields: Dict[str, Any] = {
            "error_type": self.__class__.__name__,  # class name is a stable short code
        }
        if self.error_code:
            fields["error_code"] = self.error_code
        if self.details:
            # Keep details small and non-sensitive; caller must ensure redaction if needed.
            fields["details"] = self.details
        return fields

# -------------------- HTTP-only branch (uses status_code) --------------------

class ApiError(AppError):
    """
    HTTP API errors only.
    - `status_code` has HTTP semantics; do not use it in non-HTTP domains.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details=details)
        self.status_code = status_code

    def to_log_fields(self) -> Dict[str, Any]:
        fields = super().to_log_fields()
        fields["status_code"] = self.status_code
        return fields


class ValidationError(ApiError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, status_code=400, details=details)


class NotFoundError(ApiError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, status_code=404, details=details)


# -------------------- Non-HTTP branches (NO status_code) --------------------

class DatabaseError(AppError):
    """Generic database error (non-HTTP)."""
    pass


class DatabaseConnectionError(DatabaseError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code="DB_CONN_FAIL", details=details)


class DatabaseTimeoutError(DatabaseError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code="DB_TIMEOUT", details=details)


 # --New--
class DatabaseQueryTimeoutError(DatabaseError):
    """Database query exceeded configured timeout."""
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code="DB_QUERY_TIMEOUT", details=details)

class DatabaseOperationalError(DatabaseError):
    """Low-level operational failure (connection dropped, DNS fail, etc.)."""
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code="DB_OPERATIONAL_ERROR", details=details)

# ---- New, ingestion-focused errors (non-HTTP, NO status_code) ----


class MQTTError(AppError):
    """Generic MQTT error (non-HTTP)."""
    pass


class MQTTConnectionError(MQTTError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code="MQTT_CONN_FAIL", details=details)


class MQTTTimeoutError(MQTTError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code="MQTT_TIMEOUT", details=details)


class IngestError(AppError):
    """Base class for MQTT ingestion domain errors."""
    pass

class PayloadValidationError(IngestError):
    """Missing/invalid fields, JSON/timestamp issues, etc."""
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="PAYLOAD_INVALID", details=details)

class UnknownMetricError(IngestError):
    """Metric name not recognized."""
    def __init__(self, metric: str):
        super().__init__("unknown metric", error_code="UNKNOWN_METRIC", details={"metric": metric})

class NonNumericMetricError(IngestError):
    """Metric value is not int/float."""
    def __init__(self, metric: str, value_type: str):
        super().__init__("non-numeric value", error_code="NON_NUMERIC_VALUE", details={"metric": metric, "value_type": value_type})

class MetricOutOfRangeError(IngestError):
    """Metric value out of configured min/max range."""
    def __init__(self, metric: str, value: float, expected_min: float, expected_max: float):
        super().__init__(
            "value out of range",
            error_code="VALUE_OUT_OF_RANGE",
            details={"metric": metric, "value": value, "expected_min": expected_min, "expected_max": expected_max},
        )




# -------------------- Optional helpers --------------------

def to_log_fields(exc: BaseException) -> Dict[str, Any]:
    """
    Convert any exception to logging fields:
    - AppError -> use its structured `to_log_fields()`
    - Others   -> fall back to `error_type` and short message
    """
    if isinstance(exc, AppError):
        return exc.to_log_fields()
    # Fallback for non-AppError exceptions
    msg = str(exc)
    return {"error_type": exc.__class__.__name__, "error_msg": msg[:200]}
