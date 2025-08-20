// Custom error classes
// Frontend errors
export class FeError extends Error {
  constructor(message, code = "FE_ERROR", context = undefined) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.context = context;
  }
}

// Network errors
export class NetworkError extends FeError {
  constructor(message = "Network request failed", context) {
    super(message, "NETWORK_ERROR", context);
  }
}

// API errors
export class ApiError extends FeError {
  constructor(message, status, body, context) {
    super(message || "API error", "API_ERROR", context);
    this.status = status;
    this.body = body;
  }
}