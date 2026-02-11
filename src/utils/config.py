"""
Configuration management for Multi-Agent HR Intelligence Platform
"""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # API Keys
    groq_api_key: str
    openai_api_key: Optional[str] = None

    # Database
    # Railway provides DATABASE_URL, fallback to SQLite for local dev
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./smartsupport.db")
    redis_url: str = "redis://localhost:6379/0"

    # Application
    app_name: str = "Multi-Agent HR Intelligence Platform"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("ENVIRONMENT", "development") != "production"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Railway Configuration
    port: int = int(os.getenv("PORT", 8000))  # Railway sets PORT
    railway_environment: Optional[str] = os.getenv("RAILWAY_ENVIRONMENT")

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # LLM Configuration
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 1000

    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Gradio
    gradio_share: bool = False
    gradio_server_port: int = 7860

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# For easy import
settings = get_settings()
