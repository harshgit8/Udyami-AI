"""Production logging configuration for GraphRAG Agent."""

import logging
import logging.handlers
import json
import time
import functools
from typing import Any, Dict, Optional, Callable
from datetime import datetime
from pathlib import Path

from config import Config


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'error_info'):
            log_entry['error_info'] = record.error_info
        
        if hasattr(record, 'performance_metrics'):
            log_entry['performance_metrics'] = record.performance_metrics
        
        if hasattr(record, 'request_info'):
            log_entry['request_info'] = record.request_info
        
        return json.dumps(log_entry, ensure_ascii=False)


class PerformanceLogger:
    """Performance monitoring and logging."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(f"{name}.performance")
        self.metrics: Dict[str, Any] = {}
    
    def timer(self, operation_name: str):
        """Context manager for timing operations."""
        return PerformanceTimer(self, operation_name)
    
    def log_performance(self, operation: str, duration: float, 
                       additional_metrics: Optional[Dict[str, Any]] = None) -> None:
        """Log performance metrics."""
        metrics = {
            'operation': operation,
            'duration_seconds': round(duration, 4),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if additional_metrics:
            metrics.update(additional_metrics)
        
        self.logger.info(f"Performance: {operation} completed in {duration:.4f}s",
                        extra={'performance_metrics': metrics})
        
        # Update internal metrics
        if operation not in self.metrics:
            self.metrics[operation] = {
                'count': 0,
                'total_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0
            }
        
        op_metrics = self.metrics[operation]
        op_metrics['count'] += 1
        op_metrics['total_time'] += duration
        op_metrics['min_time'] = min(op_metrics['min_time'], duration)
        op_metrics['max_time'] = max(op_metrics['max_time'], duration)
        op_metrics['avg_time'] = op_metrics['total_time'] / op_metrics['count']
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        return {
            'operations': self.metrics.copy(),
            'total_operations': sum(m['count'] for m in self.metrics.values()),
            'total_time': sum(m['total_time'] for m in self.metrics.values())
        }


class PerformanceTimer:
    """Context manager for performance timing."""
    
    def __init__(self, perf_logger: PerformanceLogger, operation_name: str):
        self.perf_logger = perf_logger
        self.operation_name = operation_name
        self.start_time: Optional[float] = None
        self.additional_metrics: Dict[str, Any] = {}
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            
            # Add exception info if present
            if exc_type is not None:
                self.additional_metrics['exception'] = {
                    'type': exc_type.__name__,
                    'message': str(exc_val)
                }
            
            self.perf_logger.log_performance(
                self.operation_name, 
                duration, 
                self.additional_metrics
            )
    
    def add_metric(self, key: str, value: Any) -> None:
        """Add additional metric to be logged."""
        self.additional_metrics[key] = value


class RequestLogger:
    """Request/response logging for API calls."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(f"{name}.requests")
    
    def log_request(self, func: Callable) -> Callable:
        """Decorator for logging requests and responses."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_id = f"req_{int(time.time() * 1000)}"
            start_time = time.time()
            
            # Log request
            request_info = {
                'request_id': request_id,
                'function': func.__name__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys()),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Request started: {func.__name__}",
                           extra={'request_info': request_info})
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful response
                duration = time.time() - start_time
                response_info = {
                    'request_id': request_id,
                    'function': func.__name__,
                    'duration_seconds': round(duration, 4),
                    'status': 'success',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                self.logger.info(f"Request completed: {func.__name__}",
                               extra={'request_info': response_info})
                
                return result
                
            except Exception as e:
                # Log error response
                duration = time.time() - start_time
                error_info = {
                    'request_id': request_id,
                    'function': func.__name__,
                    'duration_seconds': round(duration, 4),
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                self.logger.error(f"Request failed: {func.__name__}",
                                extra={'request_info': error_info})
                
                raise e
        
        return wrapper


class GraphRAGLogger:
    """Specialized logger for GraphRAG operations."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(f"{name}.graphrag")
        self.query_count = 0
        self.graph_stats = {}
    
    def log_graph_operation(self, operation: str, details: Dict[str, Any]) -> None:
        """Log graph-specific operations."""
        self.logger.info(f"Graph operation: {operation}", 
                        extra={'graph_operation': details})
    
    def log_semantic_search(self, query: str, results_count: int, 
                          processing_time: float) -> None:
        """Log semantic search operations."""
        self.query_count += 1
        
        search_info = {
            'query_id': self.query_count,
            'query_length': len(query),
            'results_count': results_count,
            'processing_time': round(processing_time, 4),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Semantic search completed: {results_count} results",
                        extra={'semantic_search': search_info})
    
    def log_formulation_generation(self, request: Dict[str, Any], 
                                 recommendations_count: int,
                                 processing_time: float) -> None:
        """Log formulation generation operations."""
        formulation_info = {
            'application': request.get('application', 'unknown'),
            'cost_limit': request.get('cost_limit', 0),
            'volume_kg': request.get('volume_kg', 0),
            'recommendations_count': recommendations_count,
            'processing_time': round(processing_time, 4),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Formulation generation: {recommendations_count} recommendations",
                        extra={'formulation_generation': formulation_info})


def setup_logging() -> None:
    """Setup production logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with simple format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with JSON format
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / Config.LOG_FILE,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'graphrag_errors.log',
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(error_handler)
    
    # Performance log handler
    perf_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'graphrag_performance.log',
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.setFormatter(JSONFormatter())
    
    # Add performance handler to performance loggers
    perf_logger = logging.getLogger('performance')
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)
    
    logging.info("GraphRAG logging system initialized")


def get_logger(name: str) -> logging.Logger:
    """Get logger instance with proper configuration."""
    return logging.getLogger(name)


def log_system_info() -> None:
    """Log system information on startup."""
    import sys
    import platform
    
    logger = get_logger(__name__)
    
    system_info = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'processor': platform.processor(),
        'architecture': platform.architecture(),
        'config': Config.to_dict()
    }
    
    logger.info("System information", extra={'system_info': system_info})


# Initialize logging on module import
setup_logging()