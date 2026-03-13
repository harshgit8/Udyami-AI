"""Core RD Agent functionality for GraphRAG system."""

from typing import Dict, List, Any, Optional
from data_layer import db_manager
from exceptions import FormulationError, ExceptionHandler
from formulation_validators import RequestValidator
from logging_config import get_logger

logger = get_logger(__name__)


class RDAgent:
    """Core RD Agent for GraphRAG system."""
    
    def __init__(self):
        """Initialize RD Agent."""
        try:
            db_manager.initialize()
            logger.info("RD Agent initialized")
        except Exception as e:
            raise FormulationError(f"Failed to initialize RD Agent: {e}")
    
    @ExceptionHandler.handle_exceptions
    def design_formulation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Design formulation using database lookup."""
        try:
            # Validate request
            validated_request = RequestValidator.validate_request(request)
            
            # Find matching formulations
            matches = self._find_matching_formulations(validated_request)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(matches, validated_request)
            
            return {
                'status': 'COMPLETE',
                'source': 'RD_AGENT',
                'validated_request': validated_request,
                'top_5_recommendations': recommendations[:5]
            }
            
        except Exception as e:
            logger.error(f"Formulation design failed: {e}")
            raise FormulationError(f"Formulation design failed: {e}")
    
    def _find_matching_formulations(self, request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find matching formulations from database."""
        application = request.get('application', '')
        cost_limit = request.get('cost_limit', 100.0)
        
        # Search by application
        app_matches = db_manager.formulation_index.find_by_application(application)
        
        # Filter by cost
        cost_matches = [fm for fm in app_matches if fm.get('cost_per_kg', 0) <= cost_limit]
        
        return cost_matches[:10]
    
    def _generate_recommendations(self, matches: List[Dict[str, Any]], 
                                request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations from matches."""
        recommendations = []
        
        if not matches:
            # Default formulation
            recommendations.append({
                'name': 'Default PVC Formulation',
                'formulation': {'PVC_K70': 100, 'DOP': 40, 'CaCO3': 8, 'Ca_Zn': 2},
                'cost_analysis': {'total_cost_per_kg': 65.0},
                'properties': {'tensile_strength_mpa': 18.0, 'elongation_percent': 200.0},
                'compliance': {'verdict': 'UNKNOWN'},
                'risk_assessment': {'risk_level': 'MEDIUM'},
                'overall_score': 0.5
            })
        else:
            for i, match in enumerate(matches):
                recommendations.append({
                    'name': f"Database Match {i+1} - {match.get('id', 'Unknown')}",
                    'formulation': match.get('formula', match.get('formulation', {})),
                    'cost_analysis': {'total_cost_per_kg': match.get('cost_per_kg', 65.0)},
                    'properties': match.get('prop', match.get('properties', {})),
                    'compliance': {'verdict': match.get('verdict', 'UNKNOWN')},
                    'risk_assessment': {'risk_level': 'LOW' if match.get('verdict') == 'PASS' else 'MEDIUM'},
                    'overall_score': 0.8 if match.get('verdict') == 'PASS' else 0.6
                })
        
        return recommendations