"""
Main FastAPI Application for MitraVerify
"""
import logging
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import sys
from pathlib import Path

# Add the project root and src directory to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

from config.settings import settings
from config.logging_config import setup_logging
from core.fusion_engine import fusion_engine
from core.exceptions import MitraVerifyException, ValidationError, AnalysisError
from api.endpoints.verification import router as verification_router
from api.endpoints.health import router as health_router
from utils.file_utils import save_upload_file_temporarily, cleanup_temp_file
from api.endpoints.multi_source import router as multi_source_router
from api.endpoints.performance import router as performance_router
from api.middleware.logging import RequestLoggingMiddleware, PerformanceLoggingMiddleware
from api.middleware.exception_handlers import setup_exception_handlers
from middleware.rate_limiter import RateLimiterMiddleware

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="MitraVerify API",
    description="AI-powered misinformation detection system for Indian digital ecosystem",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup exception handlers first
setup_exception_handlers(app)

# Add logging middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(PerformanceLoggingMiddleware, slow_request_threshold_ms=1000.0)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Secure CORS configuration
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict to needed methods only
    allow_headers=["Content-Type", "Authorization"],  # Restrict headers
)

# Add rate limiting middleware
app.add_middleware(RateLimiterMiddleware, calls=100, period=60)

# Static files and templates are not needed for backend-only API
# app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
# templates = Jinja2Templates(directory=str(templates_path)) if templates_path.exists() else None

# Include routers
app.include_router(verification_router, prefix="/api/v1", tags=["verification"])
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(multi_source_router, prefix="/api/v1", tags=["multi-source"])
app.include_router(performance_router, prefix="/api/v1", tags=["performance"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to MitraVerify API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.post("/api/v1/analyze")
async def analyze_content(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Analyze content for misinformation

    Supports both text and image analysis
    """
    try:
        # Validate input using custom exception
        if not text and not file:
            raise ValidationError(
                message="Either text or file must be provided",
                field="content",
                details={"provided_text": bool(text), "provided_file": bool(file)}
            )

        image_path = None

        try:
            # Handle file upload with async operations
            if file:
                image_path = await save_upload_file_temporarily(file)

            # Analyze content with error handling
            try:
                result = fusion_engine.analyze_content(text=text, image_path=image_path)
            except Exception as e:
                raise AnalysisError(
                    message=f"Content analysis failed: {str(e)}",
                    content_type="mixed" if text and image_path else ("text" if text else "image"),
                    details={"text_length": len(text) if text else 0, "has_image": bool(image_path)}
                )

        finally:
            # Clean up temporary file
            if image_path:
                cleanup_temp_file(image_path)

        return result

    except MitraVerifyException:
        # Re-raise custom exceptions to be handled by middleware
        raise
    except Exception as e:
        # Convert unexpected exceptions to AnalysisError
        raise AnalysisError(
            message=f"Unexpected error during analysis: {str(e)}",
            content_type="unknown",
            details={"original_error": str(e)}
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}


def main():
    """Main entry point for running the server"""
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()