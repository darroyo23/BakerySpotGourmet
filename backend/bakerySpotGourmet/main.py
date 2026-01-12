import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from bakerySpotGourmet.core.config import settings
from bakerySpotGourmet.core.logging import setup_logging
from bakerySpotGourmet.core.middleware import RequestIDMiddleware, RequestTimingMiddleware
from bakerySpotGourmet.core import exceptions
from bakerySpotGourmet.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Life span events for the application.
    """
    setup_logging()
    logger = structlog.get_logger()
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")


def get_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # Set all CORS enabled origins
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"], # TODO: Fix this to use settings.CORS_ORIGINS properly in production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Add custom middleware (order matters - first added is outermost)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    
    # Register global exception handlers
    app.add_exception_handler(exceptions.RateLimitExceededException, exceptions.rate_limit_handler)
    app.add_exception_handler(exceptions.EntityNotFoundException, exceptions.entity_not_found_handler)
    app.add_exception_handler(exceptions.BakeryException, exceptions.bakery_exception_handler)
    app.add_exception_handler(RequestValidationError, exceptions.validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, exceptions.http_exception_handler)
    app.add_exception_handler(Exception, exceptions.unhandled_exception_handler)
    
    # Health check endpoints
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    @app.get("/readiness", tags=["health"])
    async def readiness_check():
        """Readiness check endpoint."""
        return {"status": "ready"}
    
    @app.get("/liveness", tags=["health"])
    async def liveness_check():
        """Liveness check endpoint."""
        return {"status": "alive"}

    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = get_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
