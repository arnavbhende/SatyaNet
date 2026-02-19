"""
Global exception handler for SatyaNet API
Provides consistent error responses and logging
"""
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR

from core.exceptions import SatyaNetException


logger = logging.getLogger("error_handler")


async def satyanet_exception_handler(request: Request, exc: SatyaNetException) -> JSONResponse:
    """Handle custom SatyaNet exceptions"""
    
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    # Log the error with structured data
    logger.error(
        f"SatyaNet error: {exc.message}",
        extra={
            "correlation_id": correlation_id,
            "error_code": exc.error_code,
            "error_details": exc.details,
            "status_code": exc.http_status_code,
            "path": request.url.path,
            "method": request.method,
            "event": "satyanet_exception"
        }
    )
    
    # Return structured error response
    return JSONResponse(
        status_code=exc.http_status_code,
        content={
            "error": True,
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "correlation_id": correlation_id,
            "timestamp": logger.handlers[0].formatter.formatTime(logger.makeRecord(
                "", 0, "", 0, "", (), None
            )) if logger.handlers else None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    # Extract validation errors
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    # Log validation error
    logger.warning(
        f"Request validation failed: {len(validation_errors)} errors",
        extra={
            "correlation_id": correlation_id,
            "validation_errors": validation_errors,
            "path": request.url.path,
            "method": request.method,
            "event": "validation_error"
        }
    )
    
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {
                "validation_errors": validation_errors,
                "error_count": len(validation_errors)
            },
            "correlation_id": correlation_id
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    # Log HTTP exception
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "correlation_id": correlation_id,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
            "event": "http_exception"
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "details": {},
            "correlation_id": correlation_id
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    # Log unexpected error with full traceback
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "correlation_id": correlation_id,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "path": request.url.path,
            "method": request.method,
            "event": "unexpected_exception"
        },
        exc_info=True
    )
    
    # Don't expose internal error details to client
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "details": {},
            "correlation_id": correlation_id
        }
    )


def setup_exception_handlers(app):
    """Register all exception handlers with the FastAPI app"""
    
    app.add_exception_handler(SatyaNetException, satyanet_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered")
