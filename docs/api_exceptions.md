# API Exception Classes Documentation

This document describes the custom exception classes used in the backend API. Each exception maps to a specific HTTP status code and is used to provide meaningful error responses to API clients.

---

## Exception Classes

### APIException (Base Class)
- **HTTP Status:** 500
- **Description:** Generic internal server error. All custom exceptions inherit from this class.

### BadRequest
- **HTTP Status:** 400
- **Description:** The request was invalid or malformed.
- **Usage:** Use when the client sends invalid JSON, missing fields, or malformed data.

### NotFound
- **HTTP Status:** 404
- **Description:** The requested resource was not found.
- **Usage:** Use when a requested entity (e.g., device, data) does not exist.

### InvalidParameter
- **HTTP Status:** 400
- **Description:** The provided parameter is invalid or missing.
- **Usage:** Use for missing or invalid query/path parameters.

### DatabaseError
- **HTTP Status:** 503
- **Description:** A database error occurred while processing your request.
- **Usage:** Use for general database errors not covered by more specific exceptions.

### DatabaseConnectionError
- **HTTP Status:** 503
- **Description:** Could not connect to the database.
- **Usage:** Use when the database is unreachable or connection fails.

### DatabaseQueryError
- **HTTP Status:** 503
- **Description:** An error occurred while querying the database.
- **Usage:** Use for SQL errors or failed queries.

### ExternalServiceError
- **HTTP Status:** 503
- **Description:** An error occurred while communicating with an external service.
- **Usage:** Use for failures in external APIs or services (e.g., MQTT).

### DataValidationError
- **HTTP Status:** 422
- **Description:** The provided data is invalid or does not meet the required criteria.
- **Usage:** Use for failed data validation (e.g., sensor data out of range).

### RateLimitExceeded
- **HTTP Status:** 429
- **Description:** Rate limit exceeded. Please try again later.
- **Usage:** Use when a client exceeds allowed request limits.

### ServiceUnavailable
- **HTTP Status:** 503
- **Description:** The service is currently unavailable. Please try again later.
- **Usage:** Use for temporary outages or maintenance windows.

---

## Example Error Response

```json
{
  "status": "error",
  "message": "The request was invalid or malformed."
}
```

Each exception will return a JSON response with a suitable HTTP status code and a descriptive message.
