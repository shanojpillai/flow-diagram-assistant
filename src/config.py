"""
Configuration settings for Flow Diagram Animation Assistant
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # API configuration
    OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama2")
    
    # Application settings
    APP_DEBUG = os.getenv("APP_DEBUG", "False").lower() in ("true", "1", "t")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Animation settings
    ANIMATION_ENABLED = os.getenv("ANIMATION_ENABLED", "True").lower() in ("true", "1", "t")
    ANIMATION_SPEED = float(os.getenv("ANIMATION_SPEED", "1.0"))
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent.absolute()
    CACHE_DIR = Path(os.getenv("CACHE_DIR", "./cache"))
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        
        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith("__") and not callable(value)
        }
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Any: Configuration value
        """
        return getattr(cls, key, default)


# Create cache directory if it doesn't exist
Config.CACHE_DIR.mkdir(exist_ok=True, parents=True)