export class AppError extends Error {
  constructor(message, meta = {}) {
    super(message);
    this.name = this.constructor.name;
    this.meta = meta;
  }
}
export class NetworkError extends AppError {}
export class TimeoutError extends AppError {}
export class ParseError extends AppError {}

export class ApiError extends AppError {
  constructor(message, status, errorType, meta = {}) {
    super(message, { status, errorType, ...meta });
    this.status = status;
    this.errorType = errorType;
  }
}
export class ValidationError extends ApiError {}
export class NotFoundError extends ApiError {}
export class DatabaseError extends ApiError {}
export class DatabaseTimeoutError extends ApiError {}
export class GenericApiError extends ApiError {}