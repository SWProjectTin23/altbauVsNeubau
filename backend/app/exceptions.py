from werkzeug.exceptions import HTTPException

# Basis class for all API-related exceptions
class APIException(HTTPException):
    code = 500
    description ="An internal server error occurred."

# Error for invalid input data (HTTP 400 Bad Request)
class BadRequest(APIException):
    code = 400
    description = "The request was invalid or malformed."

# class NotFound(APIException):
class NotFound(APIException):
    code = 404
    description = "The requested resource was not found."

class InvalidParameter(APIException):
    code = 400
    description = "The provided parameter is invalid or missing."

# Error with Database operations (HTTP 503 Service Unavailable
class DatabaseError(APIException):
    code = 503
    description = "A database error occurred while processing your request."

class DatabaseConnectionError(APIException):
    code = 503
    description = "Could not connect to the database."

class DatabaseQueryError(APIException):
    code = 503
    description = "An error occurred while querying the database."

# Error with external services (e.g. MQTT) (HTTP 503 Service Unavailable)
class ExternalServiceError(APIException):
    code = 503
    description = "An error occurred while communicating with an external service."

# Error with Sensor data (HTTP 442 Unprocessable Entity)
class DataValidationError(APIException):
    code = 422
    description = "The provided data is invalid or does not meet the required criteria."

class RateLimitExceeded(APIException):
    code = 429
    description = "Rate limit exceeded. Please try again later."

class ServiceUnavailable(APIException):
    code = 503
    description = "The service is currently unavailable. Please try again later."