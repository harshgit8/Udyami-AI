"""Custom exceptions for RND Agent."""

from typing import Optional, Dict, Any


class RNDAgentError(Exception):
    """Base exception for RND Agent."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(RNDAgentError):
    """Configuration validation error."""
    pass


class DataValidationError(RNDAgentError):
    """Data validation error."""
    pass


class DatabaseError(RNDAgentError):
    """Database loading or access error."""
    pass


class FormulationError(RNDAgentError):
    """Formulation design error."""
    pass


class MaterialUnavailableError(RNDAgentError):
    """Material not available from suppliers."""
    pass


class ComplianceError(RNDAgentError):
    """Compliance validation error."""
    pass


class LLMError(RNDAgentError):
    """LLM service error."""
    pass


class PropertyPredictionError(RNDAgentError):
    """Property prediction model error."""
    pass


class CostCalculationError(RNDAgentError):
    """Cost calculation error."""
    pass


class SupplierError(RNDAgentError):
    """Supplier data or availability error."""
    pass


class ValidationError(RNDAgentError):
    """Input validation error."""
    pass