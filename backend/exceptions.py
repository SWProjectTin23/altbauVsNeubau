import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base class for all application errors."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code
        logger.error(f"{self.__class__.__name__}: {message} (Status: {status_code})")

class ApiError(AppError):
    """Base class for API errors."""
    pass

class ValidationError(ApiError):
    """Error raised for validation errors."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)
        logger.warning(f"ValidationError: {message}")
    
class DatabaseError(ApiError):
    """Error raised for database-related issues."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)
        logger.error(f"DatabaseError: {message}")

class NotFoundError(ApiError):
    """Error raised when a resource is not found."""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)
        logger.warning(f"NotFoundError: {message}")

class DatabaseConnectionError(DatabaseError):
    """Error raised when a database connection fails."""
    def __init__(self, message: str):
        super().__init__(message)
        logger.error(f"DatabaseConnectionError: {message}")

class DatabaseTimeoutError(DatabaseError):
    """Error raised when a database operation times out."""
    def __init__(self, message: str):
        super().__init__(message, status_code=504)
        logger.error(f"DatabaseTimeoutError: {message}")

class MQTTError(AppError):
    """Base class for MQTT-related errors."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code=status_code)
        logger.error(f"MQTTError: {message} (Status: {status_code})")

class MQTTConnectionError(MQTTError):
    """Error raised when a MQTT connection fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)
        logger.error(f"MQTTConnectionError: {message}")

class MQTTTimeoutError(MQTTError):
    """Error raised when a MQTT operation times out."""
    def __init__(self, message: str):
        super().__init__(message, status_code=504)
        logger.error(f"MQTTTimeoutError: {message}")