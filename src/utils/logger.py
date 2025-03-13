"""
Logger utility for Flow Diagram Animation Assistant
"""
import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

def setup_logger(name: str = None) -> logging.Logger:
    """
    Set up and configure logger
    
    Args:
        name: Logger name (defaults to __name__ of caller)
        
    Returns:
        logging.Logger: Configured logger
    """
    # Load environment variables
    load_dotenv()
    
    # Get logger name
    if name is None:
        # Get the name of the calling module
        import inspect
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        name = module.__name__ if module else "flow_diagram_assistant"
    
    # Create logger
    logger = logging.getLogger(name)
    
    # If logger is already configured, return it
    if logger.handlers:
        return logger
    
    # Set log level from environment variable or default to INFO
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    console_formatter = logging.Formatter(
        "%(levelname)s - %(message)s"
    )
    
    # Create and add file handler (rotating log file)
    file_handler = RotatingFileHandler(
        logs_dir / "flow_diagram_assistant.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)
    
    # Create and add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)
    
    return logger