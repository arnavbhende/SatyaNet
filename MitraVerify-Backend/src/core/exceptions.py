"""
Custom exceptions for MitraVerify application
Provides structured error handling with error codes and details
"""
from typing import Dict, Any, Optional


class MitraVerifyException(Exception):
    """Base exception for MitraVerify application"""

    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None,
        http_status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        self.http_status_code = http_status_code
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "status_code": self.http_status_code
        }


class ModelLoadError(MitraVerifyException):
    """Raised when AI model fails to load"""

    def __init__(self, message: str, model_name: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="MODEL_LOAD_ERROR",
            details={"model_name": model_name, **(details or {})},
            http_status_code=503
        )


class AnalysisError(MitraVerifyException):
    """Raised when content analysis fails"""

    def __init__(self, message: str, content_type: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="ANALYSIS_ERROR",
            details={"content_type": content_type, **(details or {})},
            http_status_code=422
        )


class ValidationError(MitraVerifyException):
    """Raised when input validation fails"""

    def __init__(self, message: str, field: str = None, value: Any = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field": field, "value": str(value) if value is not None else None, **(details or {})},
            http_status_code=400
        )


class FileProcessingError(MitraVerifyException):
    """Raised when file processing fails"""

    def __init__(self, message: str, filename: str = None, file_type: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="FILE_PROCESSING_ERROR",
            details={"filename": filename, "file_type": file_type, **(details or {})},
            http_status_code=422
        )


class ResourceExhaustedError(MitraVerifyException):
    """Raised when system resources are exhausted"""

    def __init__(self, message: str, resource_type: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="RESOURCE_EXHAUSTED",
            details={"resource_type": resource_type, **(details or {})},
            http_status_code=503
        )


class ConfigurationError(MitraVerifyException):
    """Raised when configuration is invalid"""

    def __init__(self, message: str, config_key: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details={"config_key": config_key, **(details or {})},
            http_status_code=500
        )


class ExternalServiceError(MitraVerifyException):
    """Raised when external service calls fail"""

    def __init__(self, message: str, service_name: str = None, status_code: int = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service_name": service_name, "status_code": status_code, **(details or {})},
            http_status_code=502
        )
