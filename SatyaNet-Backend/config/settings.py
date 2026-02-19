"""
Configuration settings for MitraVerify
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Model Configuration
    text_model_name: str = "google/muril-base-cased"
    image_model_name: str = "openai/clip-vit-base-patch32"
    embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

    # Data Paths
    model_cache_dir: str = "./data/models/pretrained"
    evidence_db_path: str = "./data/evidence/fact_check_corpus.json"
    image_db_path: str = "./data/evidence/image_database"

    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/mitraverify.log"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    debug: bool = True

    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://your-production-domain.com"
    ]
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [
        "image/jpeg",
        "image/png", 
        "image/webp",
        "text/plain"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False
        protected_namespaces = ()


# Global settings instance
settings = Settings()