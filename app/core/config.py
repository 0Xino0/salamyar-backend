"""Application configuration settings."""

from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Salamyar Product Search API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for searching and selecting products from Basalam marketplace"
    
    # External APIs
    BASALAM_SEARCH_URL: str = "https://search.basalam.com/ai-engine/api/v2.0/product/search"
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 12
    MAX_PAGE_SIZE: int = 50
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]  # Configure properly for production
    
    # Legacy environment variables (from old Telegram bot setup)
    BOT_TOKEN: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow extra fields to be ignored for future compatibility
        extra = "ignore"


settings = Settings()
