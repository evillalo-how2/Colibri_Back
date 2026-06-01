class AppError(Exception):
    status_code: int = 500
    code: str = "INTERNAL_SERVER_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None):
        if message:
            self.message = message


class BadRequestError(AppError):
    status_code = 400
    code = "BAD_REQUEST"
    message = "Bad request."


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"
    message = "Unauthorized."


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"
    message = "Forbidden."


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"
    message = "Resource not found."


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"
    message = "Resource conflict."


class ValidationAppError(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"
    message = "Validation error."


class DatabaseError(AppError):
    status_code = 500
    code = "DATABASE_ERROR"
    message = "Database error."
    
class TooManyRequestsError(AppError):
    status_code = 429
    code = "TOO_MANY_REQUESTS"
    message = "Too many requests."
    
class InactiveUserError(AppError):
    status_code = 403
    code = "INACTIVE_USER"
    message = "User account is inactive."