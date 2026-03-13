"""Production configuration management for GraphRAG Agent."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class ConfigError(Exception):
    """Configuration validation error."""
    pass


class Config:
    """Production-ready configuration management for GraphRAG system."""
    
    # Database configuration
    DATABASE_PATH = Path(os.getenv('GRAPHRAG_DATABASE_PATH', 'graphrag/database'))
    
    # LLM configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    LLM_MODEL = os.getenv('GRAPHRAG_LLM_MODEL', 'llama3-70b-8192')
    LLM_TEMPERATURE = float(os.getenv('GRAPHRAG_LLM_TEMPERATURE', '0.1'))
    LLM_MAX_TOKENS = int(os.getenv('GRAPHRAG_LLM_MAX_TOKENS', '2048'))
    LLM_TIMEOUT_SECONDS = int(os.getenv('GRAPHRAG_LLM_TIMEOUT', '45'))
    LLM_MAX_RETRIES = int(os.getenv('GRAPHRAG_LLM_RETRIES', '3'))
    
    # GraphRAG specific configuration
    GRAPH_EMBEDDING_DIMENSIONS = int(os.getenv('GRAPH_EMBEDDING_DIM', '100'))
    SEMANTIC_SIMILARITY_THRESHOLD = float(os.getenv('SEMANTIC_THRESHOLD', '0.1'))
    MAX_GRAPH_TRAVERSAL_DEPTH = int(os.getenv('MAX_GRAPH_DEPTH', '3'))
    GRAPH_CACHE_SIZE = int(os.getenv('GRAPH_CACHE_SIZE', '1000'))
    
    # Processing configuration
    DEFAULT_COST_LIMIT = float(os.getenv('GRAPHRAG_DEFAULT_COST_LIMIT', '70.0'))
    DEFAULT_VOLUME_KG = int(os.getenv('GRAPHRAG_DEFAULT_VOLUME_KG', '100'))
    DEFAULT_DELIVERY_DAYS = int(os.getenv('GRAPHRAG_DEFAULT_DELIVERY_DAYS', '10'))
    PROCESSING_COST_MULTIPLIER = float(os.getenv('GRAPHRAG_PROCESSING_COST_MULT', '0.05'))
    OVERHEAD_COST_MULTIPLIER = float(os.getenv('GRAPHRAG_OVERHEAD_COST_MULT', '0.03'))
    
    # Performance configuration
    CACHE_SIZE = int(os.getenv('GRAPHRAG_CACHE_SIZE', '2000'))
    BATCH_SIZE = int(os.getenv('GRAPHRAG_BATCH_SIZE', '20'))
    MAX_CONCURRENT_REQUESTS = int(os.getenv('GRAPHRAG_MAX_CONCURRENT', '10'))
    QUERY_TIMEOUT_SECONDS = int(os.getenv('GRAPHRAG_QUERY_TIMEOUT', '120'))
    
    # Logging configuration
    LOG_LEVEL = os.getenv('GRAPHRAG_LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('GRAPHRAG_LOG_FILE', 'graphrag_agent.log')
    LOG_MAX_BYTES = int(os.getenv('GRAPHRAG_LOG_MAX_BYTES', '20971520'))  # 20MB
    LOG_BACKUP_COUNT = int(os.getenv('GRAPHRAG_LOG_BACKUP_COUNT', '10'))
    
    # Quality thresholds
    MIN_TENSILE_STRENGTH = float(os.getenv('GRAPHRAG_MIN_TENSILE', '15.0'))
    MIN_ELONGATION = float(os.getenv('GRAPHRAG_MIN_ELONGATION', '150.0'))
    MAX_HARDNESS = float(os.getenv('GRAPHRAG_MAX_HARDNESS', '85.0'))
    MIN_CONFIDENCE_SCORE = float(os.getenv('GRAPHRAG_MIN_CONFIDENCE', '0.3'))
    
    # Graph construction parameters
    MATERIAL_COOCCURRENCE_THRESHOLD = int(os.getenv('MATERIAL_COOCCUR_THRESHOLD', '2'))
    SUPPLIER_RELIABILITY_THRESHOLD = float(os.getenv('SUPPLIER_RELIABILITY_THRESHOLD', '3.0'))
    PROPERTY_CORRELATION_THRESHOLD = float(os.getenv('PROPERTY_CORRELATION_THRESHOLD', '0.3'))
    
    # Semantic search parameters
    TFIDF_MAX_FEATURES = int(os.getenv('TFIDF_MAX_FEATURES', '5000'))
    TFIDF_NGRAM_RANGE = (1, 3)  # Unigrams to trigrams
    SVD_COMPONENTS = int(os.getenv('SVD_COMPONENTS', '100'))
    
    # Risk assessment parameters
    HIGH_RISK_THRESHOLD = float(os.getenv('HIGH_RISK_THRESHOLD', '0.6'))
    MEDIUM_RISK_THRESHOLD = float(os.getenv('MEDIUM_RISK_THRESHOLD', '0.3'))
    COST_RISK_MULTIPLIER = float(os.getenv('COST_RISK_MULTIPLIER', '1.2'))
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration on startup."""
        errors = []
        warnings = []
        
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
        
        if cls.SEMANTIC_SIMILARITY_THRESHOLD < 0 or cls.SEMANTIC_SIMILARITY_THRESHOLD > 1:
            errors.append(f"Invalid semantic similarity threshold: {cls.SEMANTIC_SIMILARITY_THRESHOLD}")
        
        if cls.MAX_GRAPH_TRAVERSAL_DEPTH < 1 or cls.MAX_GRAPH_TRAVERSAL_DEPTH > 10:
            errors.append(f"Invalid graph traversal depth: {cls.MAX_GRAPH_TRAVERSAL_DEPTH}")
        
        if cls.GRAPH_EMBEDDING_DIMENSIONS < 10 or cls.GRAPH_EMBEDDING_DIMENSIONS > 1000:
            errors.append(f"Invalid embedding dimensions: {cls.GRAPH_EMBEDDING_DIMENSIONS}")
        
        # Performance validations
        if cls.MAX_CONCURRENT_REQUESTS < 1 or cls.MAX_CONCURRENT_REQUESTS > 100:
            warnings.append(f"Unusual concurrent request limit: {cls.MAX_CONCURRENT_REQUESTS}")
        
        if cls.QUERY_TIMEOUT_SECONDS < 10 or cls.QUERY_TIMEOUT_SECONDS > 600:
            warnings.append(f"Unusual query timeout: {cls.QUERY_TIMEOUT_SECONDS}s")
        
        if cls.CACHE_SIZE < 100 or cls.CACHE_SIZE > 10000:
            warnings.append(f"Unusual cache size: {cls.CACHE_SIZE}")
        
        # Raise errors if any
        if errors:
            raise ConfigError(f"Configuration validation failed: {'; '.join(errors)}")
        
        # Log warnings
        for warning in warnings:
            logging.warning(f"Configuration warning: {warning}")
        
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
    def get_graph_config(cls) -> Dict[str, Any]:
        """Get graph-specific configuration."""
        return {
            'embedding_dimensions': cls.GRAPH_EMBEDDING_DIMENSIONS,
            'similarity_threshold': cls.SEMANTIC_SIMILARITY_THRESHOLD,
            'max_traversal_depth': cls.MAX_GRAPH_TRAVERSAL_DEPTH,
            'cache_size': cls.GRAPH_CACHE_SIZE,
            'material_cooccurrence_threshold': cls.MATERIAL_COOCCURRENCE_THRESHOLD,
            'supplier_reliability_threshold': cls.SUPPLIER_RELIABILITY_THRESHOLD,
            'property_correlation_threshold': cls.PROPERTY_CORRELATION_THRESHOLD
        }
    
    @classmethod
    def get_semantic_config(cls) -> Dict[str, Any]:
        """Get semantic search configuration."""
        return {
            'tfidf_max_features': cls.TFIDF_MAX_FEATURES,
            'tfidf_ngram_range': cls.TFIDF_NGRAM_RANGE,
            'svd_components': cls.SVD_COMPONENTS,
            'similarity_threshold': cls.SEMANTIC_SIMILARITY_THRESHOLD
        }
    
    @classmethod
    def get_risk_config(cls) -> Dict[str, Any]:
        """Get risk assessment configuration."""
        return {
            'high_risk_threshold': cls.HIGH_RISK_THRESHOLD,
            'medium_risk_threshold': cls.MEDIUM_RISK_THRESHOLD,
            'cost_risk_multiplier': cls.COST_RISK_MULTIPLIER
        }
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            'database_path': str(cls.DATABASE_PATH),
            'llm_model': cls.LLM_MODEL,
            'llm_temperature': cls.LLM_TEMPERATURE,
            'graph_embedding_dimensions': cls.GRAPH_EMBEDDING_DIMENSIONS,
            'semantic_similarity_threshold': cls.SEMANTIC_SIMILARITY_THRESHOLD,
            'max_graph_traversal_depth': cls.MAX_GRAPH_TRAVERSAL_DEPTH,
            'default_cost_limit': cls.DEFAULT_COST_LIMIT,
            'default_volume_kg': cls.DEFAULT_VOLUME_KG,
            'cache_size': cls.CACHE_SIZE,
            'log_level': cls.LOG_LEVEL,
            'min_confidence_score': cls.MIN_CONFIDENCE_SCORE,
            'query_timeout_seconds': cls.QUERY_TIMEOUT_SECONDS
        }
    
    @classmethod
    def update_from_dict(cls, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary (for testing)."""
        for key, value in config_dict.items():
            if hasattr(cls, key.upper()):
                setattr(cls, key.upper(), value)
    
    @classmethod
    def get_performance_limits(cls) -> Dict[str, Any]:
        """Get performance-related limits."""
        return {
            'max_concurrent_requests': cls.MAX_CONCURRENT_REQUESTS,
            'query_timeout_seconds': cls.QUERY_TIMEOUT_SECONDS,
            'cache_size': cls.CACHE_SIZE,
            'batch_size': cls.BATCH_SIZE,
            'llm_timeout_seconds': cls.LLM_TIMEOUT_SECONDS,
            'llm_max_retries': cls.LLM_MAX_RETRIES
        }