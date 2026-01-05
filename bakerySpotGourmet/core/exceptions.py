"""
Global exceptions and exception handlers for BakerySpotGourmet.
"""
import structlog
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = structlog.get_logger()


class BakeryException(Exception):
    """Base exception for BakerySpotGourmet."""
    pass


class EntityNotFoundException(BakeryException):
    """Raised when an entity is not found in the database."""
    def __init__(self, entity: str, identifier: str):
        self.message = f"{entity} with id {identifier} not found"
        super().__init__(self.message)


class BusinessRuleException(BakeryException):
    """Raised when a business rule is violated."""
    def __init__(self, message: str):
        super().__init__(message)


class RateLimitExceededException(BakeryException):
    """Raised when rate limit is exceeded."""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")


class IdempotencyConflictException(BakeryException):
    """Raised when idempotency key conflict is detected."""
    def __init__(self, message: str = "Idempotency key conflict"):
        super().__init__(message)


# Global Exception Handlers

async def bakery_exception_handler(request: Request, exc: BakeryException) -> JSONResponse:
    """
    Handle custom BakeryException instances.
    Returns safe, non-revealing error messages.
    """
    logger.error(
        "bakery_exception",
        exception_type=type(exc).__name__,
        message=str(exc),
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def entity_not_found_handler(request: Request, exc: EntityNotFoundException) -> JSONResponse:
    """Handle EntityNotFoundException with 404 status."""
    logger.warning(
        "entity_not_found",
        message=exc.message,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def rate_limit_handler(request: Request, exc: RateLimitExceededException) -> JSONResponse:
    """Handle rate limit exceeded with 429 status and Retry-After header."""
    logger.warning(
        "rate_limit_exceeded",
        path=request.url.path,
        retry_after=exc.retry_after,
    )
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": str(exc)},
        headers={"Retry-After": str(exc.retry_after)},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle request validation errors.
    Returns structured validation errors without exposing internal details.
    """
    logger.warning(
        "validation_error",
        path=request.url.path,
        errors=exc.errors(),
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.
    Ensures consistent error response format.
    """
    logger.warning(
        "http_exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions.
    Returns safe error message without exposing internal details.
    """
    logger.error(
        "unhandled_exception",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=request.url.path,
        exc_info=True,
    )
    
    # Return safe, non-revealing error message
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred. Please try again later."},
    )
