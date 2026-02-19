"""
Request logging middleware for MitraVerify
Provides structured logging with correlation IDs and performance tracking
"""
import uuid
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from core.exceptions import MitraVerifyException


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request logging with correlation IDs"""

    def __init__(self, app, logger_name: str = "request_logger"):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique correlation ID for this request
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Record start time
        start_time = time.time()
        
        # Extract request details
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request start
        self.logger.info(
            "Request started",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "content_length": request.headers.get("content-length"),
                "event": "request_start"
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log successful request completion
            self.logger.info(
                "Request completed successfully",
                extra={
                    "correlation_id": correlation_id,
                    "status_code": response.status_code,
                    "processing_time_ms": round(processing_time * 1000, 2),
                    "response_size": getattr(response, 'headers', {}).get('content-length'),
                    "event": "request_success"
                }
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Processing-Time"] = f"{processing_time:.3f}"
            
            return response
            
        except MitraVerifyException as e:
            # Handle custom application exceptions
            processing_time = time.time() - start_time
            
            self.logger.error(
                f"Application error: {e.message}",
                extra={
                    "correlation_id": correlation_id,
                    "error_code": e.error_code,
                    "error_details": e.details,
                    "status_code": e.http_status_code,
                    "processing_time_ms": round(processing_time * 1000, 2),
                    "event": "application_error"
                }
            )
            
            # Re-raise to be handled by exception handler
            raise
            
        except Exception as e:
            # Handle unexpected errors
            processing_time = time.time() - start_time
            
            self.logger.error(
                f"Unexpected error: {str(e)}",
                extra={
                    "correlation_id": correlation_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "processing_time_ms": round(processing_time * 1000, 2),
                    "event": "unexpected_error"
                },
                exc_info=True
            )
            
            # Re-raise to be handled by exception handler
            raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to client IP
        return request.client.host if request.client else "unknown"


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and alerting"""

    def __init__(self, app, slow_request_threshold_ms: float = 1000.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold_ms / 1000.0  # Convert to seconds
        self.logger = logging.getLogger("performance_logger")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            processing_time = time.time() - start_time
            
            # Log performance metrics
            self.logger.info(
                "Performance metrics",
                extra={
                    "correlation_id": getattr(request.state, 'correlation_id', 'unknown'),
                    "method": request.method,
                    "path": request.url.path,
                    "processing_time_ms": round(processing_time * 1000, 2),
                    "status_code": response.status_code,
                    "is_slow": processing_time > self.slow_request_threshold,
                    "event": "performance_metric"
                }
            )
            
            # Alert on slow requests
            if processing_time > self.slow_request_threshold:
                self.logger.warning(
                    f"Slow request detected: {request.method} {request.url.path}",
                    extra={
                        "correlation_id": getattr(request.state, 'correlation_id', 'unknown'),
                        "processing_time_ms": round(processing_time * 1000, 2),
                        "threshold_ms": self.slow_request_threshold * 1000,
                        "event": "slow_request_alert"
                    }
                )
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            self.logger.error(
                f"Request failed after {processing_time:.3f}s: {str(e)}",
                extra={
                    "correlation_id": getattr(request.state, 'correlation_id', 'unknown'),
                    "method": request.method,
                    "path": request.url.path,
                    "processing_time_ms": round(processing_time * 1000, 2),
                    "event": "performance_error"
                }
            )
            
            raise
