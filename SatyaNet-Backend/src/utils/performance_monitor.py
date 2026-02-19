"""
Performance Monitoring Utility
"""
import time
import psutil
import logging
from typing import Dict, Any
from functools import wraps

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor system performance and API response times"""
    
    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """Get current system performance stats"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "timestamp": time.time()
        }
    
    @staticmethod
    def timing_decorator(func):
        """Decorator to measure function execution time"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
                raise
        return wrapper

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
