"""
Model Configuration Management
"""
from typing import Dict, Any, Optional
import torch
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for AI models"""
    model_name: str
    device: str
    batch_size: int
    max_length: int
    confidence_threshold: float
    cache_enabled: bool
    temperature: float = 1.0
    top_k: Optional[int] = None
    top_p: Optional[float] = None

class ModelManager:
    """Manages model configurations and loading strategies"""
    
    # Default configurations for different model types
    DEFAULT_CONFIGS = {
        "text_analysis": ModelConfig(
            model_name="google/muril-base-cased",
            device="cuda" if torch.cuda.is_available() else "cpu",
            batch_size=16,
            max_length=512,
            confidence_threshold=0.6,
            cache_enabled=True
        ),
        "image_analysis": ModelConfig(
            model_name="openai/clip-vit-base-patch32",
            device="cuda" if torch.cuda.is_available() else "cpu",
            batch_size=8,
            max_length=77,
            confidence_threshold=0.7,
            cache_enabled=True
        ),
        "embedding": ModelConfig(
            model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
            device="cuda" if torch.cuda.is_available() else "cpu",
            batch_size=32,
            max_length=512,
            confidence_threshold=0.8,
            cache_enabled=True
        )
    }
    
    @classmethod
    def get_config(cls, model_type: str) -> ModelConfig:
        """Get configuration for a specific model type"""
        if model_type not in cls.DEFAULT_CONFIGS:
            raise ValueError(f"Unknown model type: {model_type}")
        return cls.DEFAULT_CONFIGS[model_type]
    
    @classmethod
    def update_config(cls, model_type: str, **kwargs) -> None:
        """Update configuration for a specific model type"""
        if model_type not in cls.DEFAULT_CONFIGS:
            raise ValueError(f"Unknown model type: {model_type}")
        
        config = cls.DEFAULT_CONFIGS[model_type]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                raise ValueError(f"Invalid config parameter: {key}")
    
    @classmethod
    def get_optimal_batch_size(cls, model_type: str, available_memory_gb: float) -> int:
        """Calculate optimal batch size based on available memory"""
        base_config = cls.get_config(model_type)
        
        # Simple heuristic: adjust batch size based on available memory
        if available_memory_gb >= 16:
            return base_config.batch_size
        elif available_memory_gb >= 8:
            return max(base_config.batch_size // 2, 4)
        else:
            return max(base_config.batch_size // 4, 1)

# Global model manager instance
model_manager = ModelManager()
