"""
File upload utilities for MitraVerify
Handles async file operations with proper validation and cleanup
"""
import os
import uuid
import tempfile
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException

from config.settings import settings


async def save_upload_file_temporarily(upload_file: UploadFile) -> str:
    """
    Save uploaded file temporarily with proper validation and async operations
    
    Args:
        upload_file: The uploaded file from FastAPI
        
    Returns:
        str: Path to the saved temporary file
        
    Raises:
        HTTPException: If file validation fails or upload fails
    """
    # Validate file size
    if upload_file.size and upload_file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413, 
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size / (1024*1024):.1f}MB"
        )
    
    # Validate file type
    if upload_file.content_type not in settings.allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(settings.allowed_file_types)}"
        )
    
    # Generate unique filename
    suffix = Path(upload_file.filename).suffix if upload_file.filename else ".tmp"
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"upload_{uuid.uuid4().hex}{suffix}")
    
    try:
        # Use async file operations for better performance
        async with aiofiles.open(temp_path, 'wb') as f:
            # Read file in chunks to handle large files efficiently
            chunk_size = 64 * 1024  # 64KB chunks
            while True:
                chunk = await upload_file.read(chunk_size)
                if not chunk:
                    break
                await f.write(chunk)
        
        # Reset file position for potential reuse
        await upload_file.seek(0)
        
        return temp_path
        
    except Exception as e:
        # Clean up temporary file if upload fails
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass  # File might not exist or permission denied
        
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )


def cleanup_temp_file(file_path: str) -> bool:
    """
    Clean up temporary file safely
    
    Args:
        file_path: Path to the temporary file to clean up
        
    Returns:
        bool: True if cleanup was successful, False otherwise
    """
    if not file_path or not os.path.exists(file_path):
        return True  # Nothing to clean up
    
    try:
        os.unlink(file_path)
        return True
    except OSError as e:
        # Log error but don't raise - cleanup failures shouldn't break the flow
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to cleanup temporary file {file_path}: {e}")
        return False


async def validate_file_content(file_path: str, expected_type: str) -> bool:
    """
    Validate actual file content against expected type
    
    Args:
        file_path: Path to the file to validate
        expected_type: Expected MIME type (e.g., 'image', 'text')
        
    Returns:
        bool: True if content matches expected type
    """
    try:
        if expected_type == "image":
            # Use PIL to validate image content
            from PIL import Image
            with Image.open(file_path) as img:
                img.verify()
            return True
        elif expected_type == "text":
            # Try to read as text file
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                await f.read(1024)  # Read first 1KB to validate
            return True
        return False
    except Exception:
        return False
