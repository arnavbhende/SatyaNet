"""
Model Optimization Utilities
"""
import torch
import gc
import logging
from typing import Dict, Any, Optional
import psutil

logger = logging.getLogger(__name__)

class ModelOptimizer:
    """Utilities for optimizing model performance"""
    
    @staticmethod
    def optimize_memory_usage() -> Dict[str, Any]:
        """Optimize memory usage and return optimization stats"""
        stats = {
            "before": {
                "gpu_memory": ModelOptimizer._get_gpu_memory(),
                "cpu_memory": psutil.virtual_memory().percent
            }
        }
        
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("Cleared CUDA cache")
        
        # Force garbage collection
        gc.collect()
        
        stats["after"] = {
            "gpu_memory": ModelOptimizer._get_gpu_memory(),
            "cpu_memory": psutil.virtual_memory().percent
        }
        
        stats["improvement"] = {
            "gpu_freed": stats["before"]["gpu_memory"] - stats["after"]["gpu_memory"],
            "cpu_freed": stats["before"]["cpu_memory"] - stats["after"]["cpu_memory"]
        }
        
        return stats
    
    @staticmethod
    def _get_gpu_memory() -> float:
        """Get current GPU memory usage in GB"""
        if not torch.cuda.is_available():
            return 0.0
        
        return torch.cuda.memory_allocated() / 1024**3  # Convert to GB
    
    @staticmethod
    def enable_mixed_precision(model: torch.nn.Module) -> torch.nn.Module:
        """Enable automatic mixed precision for faster training/inference"""
        if torch.cuda.is_available():
            model = model.half()  # Convert to FP16
            logger.info("Enabled mixed precision (FP16)")
        return model
    
    @staticmethod
    def optimize_inference_speed(model: torch.nn.Module) -> torch.nn.Module:
        """Apply various optimizations for inference speed"""
        # Set model to evaluation mode
        model.eval()
        
        # Disable gradient calculation
        for param in model.parameters():
            param.requires_grad = False
        
        # Enable torch.compile if available (PyTorch 2.0+)
        if hasattr(torch, 'compile'):
            try:
                model = torch.compile(model)
                logger.info("Enabled torch.compile for faster inference")
            except Exception as e:
                logger.warning(f"Could not enable torch.compile: {e}")
        
        return model
    
    @staticmethod
    def get_model_size(model: torch.nn.Module) -> Dict[str, Any]:
        """Calculate model size and memory requirements"""
        param_size = 0
        buffer_size = 0
        
        for param in model.parameters():
            param_size += param.nelement() * param.element_size()
        
        for buffer in model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        
        total_size = (param_size + buffer_size) / 1024**2  # Convert to MB
        
        return {
            "parameters_mb": param_size / 1024**2,
            "buffers_mb": buffer_size / 1024**2,
            "total_mb": total_size,
            "total_gb": total_size / 1024
        }
    
    @staticmethod
    def benchmark_model(model: torch.nn.Module, input_tensor: torch.Tensor, num_runs: int = 100) -> Dict[str, float]:
        """Benchmark model inference speed"""
        model.eval()
        
        # Warm up
        with torch.no_grad():
            for _ in range(10):
                _ = model(input_tensor)
        
        # Benchmark
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        
        import time
        start_time = time.time()
        
        with torch.no_grad():
            for _ in range(num_runs):
                _ = model(input_tensor)
        
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        
        end_time = time.time()
        
        avg_time = (end_time - start_time) / num_runs
        throughput = num_runs / (end_time - start_time)
        
        return {
            "avg_inference_time_ms": avg_time * 1000,
            "throughput_samples_per_sec": throughput,
            "total_time_sec": end_time - start_time
        }

# Global optimizer instance
model_optimizer = ModelOptimizer()
