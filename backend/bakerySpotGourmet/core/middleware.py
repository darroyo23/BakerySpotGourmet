"""
Middleware for request handling.
Includes request ID generation, timing, and logging context injection.
"""
import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from bakerySpotGourmet.core.constants import REQUEST_ID_HEADER


logger = structlog.get_logger()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and propagate request IDs.
    Binds request_id to structured logging context for traceability.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Generate or extract request ID and add to logging context.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            
        Returns:
            Response with X-Request-ID header
        """
        # Get or generate request ID
        request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid.uuid4()))
        
        # Bind to logging context for all subsequent logs
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        # Store in request state for access in dependencies
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers[REQUEST_ID_HEADER] = request_id
        
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request timing and basic request info.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Time the request and log completion.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            
        Returns:
            Response object
        """
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log completion
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_seconds=round(duration, 3),
        )
        
        return response
