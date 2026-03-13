"""Production configuration management for RND Agent."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class ConfigError(Exception):
    """Configuration validation error."""
    pass


class Config:
    """Production-ready configuration management."""
    
    # Database configuration
    DATABASE_PATH = Path(os.getenv('RND_DATABASE_PATH', './database'))
    
    # LLM configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    LLM_MODEL = os.getenv('RND_LLM_MODEL', 'llama3-70b-8192')
    LLM_TEMPERATURE = float(os.getenv('RND_LLM_TEMPERATURE', '0.1'))
    LLM_MAX_TOKENS = int(os.getenv('RND_LLM_MAX_TOKENS', '1024'))
    LLM_TIMEOUT_SECONDS = int(os.getenv('RND_LLM_TIMEOUT', '30'))
    LLM_MAX_RETRIES = int(os.getenv('RND_LLM_RETRIES', '3'))
    
    # Processing configuration
    DEFAULT_COST_LIMIT = float(os.getenv('RND_DEFAULT_COST_LIMIT', '70.0'))
    DEFAULT_VOLUME_KG = int(os.getenv('RND_DEFAULT_VOLUME_KG', '100'))
    DEFAULT_DELIVERY_DAYS = int(os.getenv('RND_DEFAULT_DELIVERY_DAYS', '10'))
    PROCESSING_COST_MULTIPLIER = float(os.getenv('RND_PROCESSING_COST_MULT', '0.05'))
    OVERHEAD_COST_MULTIPLIER = float(os.getenv('RND_OVERHEAD_COST_MULT', '0.03'))
    
    # Performance configuration
    CACHE_SIZE = int(os.getenv('RND_CACHE_SIZE', '1000'))
    BATCH_SIZE = int(os.getenv('RND_BATCH_SIZE', '10'))
    MAX_CONCURRENT_REQUESTS = int(os.getenv('RND_MAX_CONCURRENT', '5'))
    
    # Logging configuration
    LOG_LEVEL = os.getenv('RND_LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('RND_LOG_FILE', 'rnd_agent.log')
    LOG_MAX_BYTES = int(os.getenv('RND_LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('RND_LOG_BACKUP_COUNT', '5'))
    
    # Quality thresholds
    MIN_TENSILE_STRENGTH = float(os.getenv('RND_MIN_TENSILE', '15.0'))
    MIN_ELONGATION = float(os.getenv('RND_MIN_ELONGATION', '150.0'))
    MAX_HARDNESS = float(os.getenv('RND_MAX_HARDNESS', '85.0'))
    MIN_CONFIDENCE_SCORE = float(os.getenv('RND_MIN_CONFIDENCE', '0.7'))
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration on startup."""
        errors = []
        
        # Validate database path
        if not cls.DATABASE_PATH.exists():
            errors.append(f"Database path not found: {cls.DATABASE_PATH}")
        
        # Validate required files
        required_files = [
            'chemical_ingredients.json',
            'formulations_history.json',
            'suppliers.json',
            'compliance_standards.json',
            'defect_solutions.json',
            'process_params.json'
        ]
        
        for file in required_files:
            file_path = cls.DATABASE_PATH / file
            if not file_path.exists():
                errors.append(f"Required database file missing: {file_path}")
        
        # Validate numeric ranges
        if cls.DEFAULT_COST_LIMIT <= 0:
            errors.append(f"Invalid cost limit: {cls.DEFAULT_COST_LIMIT}")
        
        if cls.DEFAULT_VOLUME_KG <= 0:
            errors.append(f"Invalid volume: {cls.DEFAULT_VOLUME_KG}")
        
        if cls.LLM_TEMPERATURE < 0 or cls.LLM_TEMPERATURE > 2:
            errors.append(f"Invalid LLM temperature: {cls.LLM_TEMPERATURE}")
        
        if cls.MIN_CONFIDENCE_SCORE < 0 or cls.MIN_CONFIDENCE_SCORE > 1:
            errors.append(f"Invalid confidence threshold: {cls.MIN_CONFIDENCE_SCORE}")
        
        if errors:
            raise ConfigError(f"Configuration validation failed: {'; '.join(errors)}")
        
        # Warn about missing optional config
        if not cls.GROQ_API_KEY:
            logging.warning("GROQ_API_KEY not set - LLM features will be disabled")
    
    @classmethod
    def get_database_files(cls) -> Dict[str, Path]:
        """Get all database file paths."""
        return {
            'ingredients': cls.DATABASE_PATH / 'chemical_ingredients.json',
            'formulations': cls.DATABASE_PATH / 'formulations_history.json',
            'suppliers': cls.DATABASE_PATH / 'suppliers.json',
            'standards': cls.DATABASE_PATH / 'compliance_standards.json',
            'defects': cls.DATABASE_PATH / 'defect_solutions.json',
            'process_params': cls.DATABASE_PATH / 'process_params.json'
        }
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            'database_path': str(cls.DATABASE_PATH),
            'llm_model': cls.LLM_MODEL,
            'llm_temperature': cls.LLM_TEMPERATURE,
            'default_cost_limit': cls.DEFAULT_COST_LIMIT,
            'default_volume_kg': cls.DEFAULT_VOLUME_KG,
            'cache_size': cls.CACHE_SIZE,
            'log_level': cls.LOG_LEVEL,
            'min_confidence_score': cls.MIN_CONFIDENCE_SCORE
        }