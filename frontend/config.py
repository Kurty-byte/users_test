"""
Configuration management for the PyQt6 frontend application.
"""
import os
from typing import Optional


class Config:
    """Configuration class for frontend application"""
    
    # API Configuration
    API_BASE_URL: str = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000/api')
    API_TIMEOUT: int = int(os.getenv('API_TIMEOUT', '10'))
    API_RETRIES: int = int(os.getenv('API_RETRIES', '3'))
    
    # Application Configuration
    APP_NAME: str = "Django User Management"
    APP_VERSION: str = "1.0.0"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: Optional[str] = os.getenv('LOG_FILE')
    
    # UI Configuration
    WINDOW_WIDTH: int = int(os.getenv('WINDOW_WIDTH', '800'))
    WINDOW_HEIGHT: int = int(os.getenv('WINDOW_HEIGHT', '600'))
    
    # Security Configuration
    TOKEN_STORAGE_KEY: str = "auth_token"
    
    @classmethod
    def get_api_url(cls) -> str:
        """Get the API base URL"""
        return cls.API_BASE_URL
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'development'
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'


# Global config instance
config = Config()
