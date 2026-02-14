"""
Performance Monitoring Endpoints
"""
from fastapi import APIRouter
from typing import Dict, Any
import logging

from core.cache_manager import cache_manager
from utils.performance_monitor import performance_monitor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/performance", tags=["performance"])

@router.get("/stats")
async def get_performance_stats():
    """Get system performance statistics"""
    try:
        system_stats = performance_monitor.get_system_stats()
        cache_stats = cache_manager.get_stats()
        
        return {
            "status": "healthy",
            "timestamp": system_stats["timestamp"],
            "system": {
                "cpu_percent": system_stats["cpu_percent"],
                "memory_percent": system_stats["memory_percent"],
                "disk_usage": system_stats["disk_usage"]
            },
            "cache": cache_stats,
            "endpoints": {
                "verification": "/api/v1/verify",
                "multi_source": "/api/v1/multi-source",
                "health": "/api/v1/health"
            }
        }
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@router.post("/cache/clear")
async def clear_cache():
    """Clear application cache"""
    try:
        cache_manager.clear()
        return {
            "status": "success",
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
