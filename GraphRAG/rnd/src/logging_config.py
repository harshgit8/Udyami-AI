"""Production logging configuration for RND Agent."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from .config import Config


class ProductionLogger:
    """Production-ready logging setup."""
    
    _logger: Optional[logging.Logger] = None
    
    @classmethod
    def setup(cls, name: str = 'rnd_agent') -> logging.Logger:
        """Setup production logging with rotation and formatting."""
        if cls._logger is not None:
            return cls._logger
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler with rotation
        log_path = Path(Config.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=Config.LOG_MAX_BYTES,
            backupCount=Config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        
        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
        logger.addHandler(console_handler)
        
        # Error handler for critical issues
        error_handler = logging.StreamHandler(sys.stderr)
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)
        
        cls._logger = logger
        logger.info(f"Production logging initialized - Level: {Config.LOG_LEVEL}")
        
        return logger
    
    @classmethod
    def get_logger(cls, name: str = 'rnd_agent') -> logging.Logger:
        """Get configured logger instance."""
        if cls._logger is None:
            return cls.setup(name)
        return cls._logger


# Convenience function
def get_logger(name: str = 'rnd_agent') -> logging.Logger:
    """Get production logger instance."""
    return ProductionLogger.get_logger(name)