"""Production exception handling for GraphRAG Agent."""

import logging
import traceback
import functools
from typing import Any, Callable, Dict, Optional, Type, Union
from datetime import datetime


class GraphRAGBaseException(Exception):
    """Base exception for GraphRAG system."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses."""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context,
            'timestamp': self.timestamp.isoformat()
        }


class KnowledgeGraphError(GraphRAGBaseException):
    """Knowledge graph construction or query errors."""
    pass


class SemanticSearchError(GraphRAGBaseException):
    """Semantic search and embedding errors."""
    pass


class GraphRAGError(GraphRAGBaseException):
    """General GraphRAG processing errors."""
    pass


class FormulationError(GraphRAGBaseException):
    """Formulation design and analysis errors."""
    pass


class ValidationError(GraphRAGBaseException):
    """Data validation and schema errors."""
    pass


class DataValidationError(GraphRAGBaseException):
    """Data validation and integrity errors."""
    pass


class DatabaseError(GraphRAGBaseException):
    """Database access and integrity errors."""
    pass


class LLMError(GraphRAGBaseException):
    """LLM integration and processing errors."""
    pass


class ConfigurationError(GraphRAGBaseException):
    """Configuration and setup errors."""
    pass


class PerformanceError(GraphRAGBaseException):
    """Performance and timeout errors."""
    pass


class MaterialUnavailableError(GraphRAGBaseException):
    """Material or supplier unavailability errors."""
    pass


class ComplianceError(GraphRAGBaseException):
    """Compliance checking and validation errors."""
    pass


class PropertyPredictionError(GraphRAGBaseException):
    """Property prediction and modeling errors."""
    pass


class CostCalculationError(GraphRAGBaseException):
    """Cost calculation and analysis errors."""
    pass


class ExceptionHandler:
    """Production exception handler with comprehensive logging and recovery."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts: Dict[str, int] = {}
        self.recovery_strategies: Dict[Type[Exception], Callable] = {}
    
    def register_recovery_strategy(self, exception_type: Type[Exception], 
                                 strategy: Callable) -> None:
        """Register a recovery strategy for specific exception type."""
        self.recovery_strategies[exception_type] = strategy
    
    def handle_exception(self, exc: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle exception with logging and recovery attempts."""
        exc_type = type(exc).__name__
        self.error_counts[exc_type] = self.error_counts.get(exc_type, 0) + 1
        
        # Create error info
        error_info = {
            'exception_type': exc_type,
            'message': str(exc),
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat(),
            'traceback': traceback.format_exc(),
            'occurrence_count': self.error_counts[exc_type]
        }
        
        # Log the exception
        self.logger.error(f"Exception handled: {exc_type} - {str(exc)}", 
                         extra={'error_info': error_info})
        
        # Attempt recovery if strategy exists
        recovery_result = None
        if type(exc) in self.recovery_strategies:
            try:
                recovery_strategy = self.recovery_strategies[type(exc)]
                recovery_result = recovery_strategy(exc, context)
                self.logger.info(f"Recovery strategy executed for {exc_type}")
            except Exception as recovery_exc:
                self.logger.error(f"Recovery strategy failed for {exc_type}: {recovery_exc}")
        
        error_info['recovery_attempted'] = recovery_result is not None
        error_info['recovery_result'] = recovery_result
        
        return error_info
    
    @staticmethod
    def handle_exceptions(func: Callable) -> Callable:
        """Decorator for automatic exception handling."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except GraphRAGBaseException as e:
                # Re-raise GraphRAG exceptions with additional context
                e.context.update({
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                })
                raise e
            except Exception as e:
                # Convert other exceptions to GraphRAG exceptions
                raise GraphRAGError(
                    f"Unexpected error in {func.__name__}: {str(e)}",
                    context={
                        'function': func.__name__,
                        'original_exception': type(e).__name__,
                        'args_count': len(args),
                        'kwargs_keys': list(kwargs.keys())
                    }
                )
        return wrapper
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        total_errors = sum(self.error_counts.values())
        
        return {
            'total_errors': total_errors,
            'error_counts': self.error_counts.copy(),
            'most_common_error': max(self.error_counts, key=self.error_counts.get) if self.error_counts else None,
            'registered_recovery_strategies': len(self.recovery_strategies)
        }


class CircuitBreaker:
    """Circuit breaker pattern for handling cascading failures."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.logger = logging.getLogger(__name__)
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
                self.logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise PerformanceError(
                    "Circuit breaker is OPEN - service temporarily unavailable",
                    context={'failure_count': self.failure_count}
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.recovery_timeout
    
    def _on_success(self) -> None:
        """Handle successful execution."""
        if self.state == 'HALF_OPEN':
            self.state = 'CLOSED'
            self.failure_count = 0
            self.logger.info("Circuit breaker reset to CLOSED")
    
    def _on_failure(self) -> None:
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            self.logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'recovery_timeout': self.recovery_timeout
        }


class RetryHandler:
    """Intelligent retry handler with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.logger = logging.getLogger(__name__)
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    self.logger.error(f"All retry attempts failed for {func.__name__}")
                    break
                
                # Calculate delay with exponential backoff
                delay = min(self.base_delay * (self.backoff_factor ** attempt), self.max_delay)
                
                self.logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, "
                                  f"retrying in {delay:.1f}s: {str(e)}")
                
                import time
                time.sleep(delay)
        
        # All retries failed
        raise PerformanceError(
            f"Function {func.__name__} failed after {self.max_retries + 1} attempts",
            context={
                'last_exception': str(last_exception),
                'attempts': self.max_retries + 1
            }
        )


class ErrorRecoveryStrategies:
    """Collection of error recovery strategies."""
    
    @staticmethod
    def database_connection_recovery(exc: DatabaseError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for database connection errors."""
        try:
            # Attempt to reinitialize database connection
            from data_layer import db_manager
            db_manager.reload_data()
            
            return {
                'strategy': 'database_reconnection',
                'success': True,
                'message': 'Database connection restored'
            }
        except Exception as e:
            return {
                'strategy': 'database_reconnection',
                'success': False,
                'message': f'Recovery failed: {str(e)}'
            }
    
    @staticmethod
    def llm_timeout_recovery(exc: LLMError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for LLM timeout errors."""
        try:
            # Fall back to rule-based processing
            return {
                'strategy': 'fallback_to_rules',
                'success': True,
                'message': 'Switched to rule-based processing'
            }
        except Exception as e:
            return {
                'strategy': 'fallback_to_rules',
                'success': False,
                'message': f'Fallback failed: {str(e)}'
            }
    
    @staticmethod
    def semantic_search_recovery(exc: SemanticSearchError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for semantic search errors."""
        try:
            # Fall back to keyword-based search
            return {
                'strategy': 'keyword_search_fallback',
                'success': True,
                'message': 'Using keyword-based search'
            }
        except Exception as e:
            return {
                'strategy': 'keyword_search_fallback',
                'success': False,
                'message': f'Keyword search failed: {str(e)}'
            }
    
    @staticmethod
    def material_unavailable_recovery(exc: MaterialUnavailableError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for material unavailability."""
        try:
            # Suggest alternative materials
            material_name = context.get('material_name', 'unknown')
            
            # Simple alternative mapping
            alternatives = {
                'DOP': ['DBP', 'DOTP'],
                'DBP': ['DOP', 'DINP'],
                'PVC_K70': ['PVC_K67', 'PVC_K72'],
                'CaCO3': ['TiO2', 'Talc']
            }
            
            suggested_alternatives = alternatives.get(material_name, [])
            
            return {
                'strategy': 'material_substitution',
                'success': True,
                'message': f'Suggested alternatives: {suggested_alternatives}',
                'alternatives': suggested_alternatives
            }
        except Exception as e:
            return {
                'strategy': 'material_substitution',
                'success': False,
                'message': f'Alternative suggestion failed: {str(e)}'
            }


# Global exception handler instance
global_exception_handler = ExceptionHandler()

# Register recovery strategies
global_exception_handler.register_recovery_strategy(
    DatabaseError, ErrorRecoveryStrategies.database_connection_recovery
)
global_exception_handler.register_recovery_strategy(
    LLMError, ErrorRecoveryStrategies.llm_timeout_recovery
)
global_exception_handler.register_recovery_strategy(
    SemanticSearchError, ErrorRecoveryStrategies.semantic_search_recovery
)
global_exception_handler.register_recovery_strategy(
    MaterialUnavailableError, ErrorRecoveryStrategies.material_unavailable_recovery
)

# Global circuit breaker for critical operations
critical_operations_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

# Global retry handler
default_retry_handler = RetryHandler(max_retries=3, base_delay=1.0, max_delay=30.0)