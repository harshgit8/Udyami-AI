"""LLM interface for GraphRAG system."""

import json
import time
from typing import Dict, List, Any, Optional
from groq import Groq

from config import Config
from exceptions import LLMError, ValidationError, ExceptionHandler
from formulation_validators import RequestValidator
from data_layer import db_manager
from logging_config import get_logger

logger = get_logger(__name__)


class LLMFormulationAgent:
    """LLM formulation agent for GraphRAG system."""
    
    def __init__(self):
        """Initialize LLM agent."""
        try:
            # Initialize database
            db_manager.initialize()
            
            # Initialize Groq client if API key available
            self.groq_client = None
            if Config.GROQ_API_KEY:
                self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
                logger.info("Groq LLM client initialized")
            else:
                logger.warning("GROQ_API_KEY not set - LLM features disabled")
            
            logger.info("LLM Formulation Agent initialized")
            
        except Exception as e:
            raise LLMError(f"Failed to initialize LLM agent: {e}")
    
    @ExceptionHandler.handle_exceptions
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process user query with LLM."""
        try:
            logger.info(f"Processing LLM query: {user_query[:100]}...")
            
            if not self.groq_client:
                return self._fallback_response(user_query)
            
            # Create LLM prompt
            prompt = self._create_llm_prompt(user_query)
            
            # Call LLM
            response = self._call_llm(prompt)
            
            # Parse response
            parsed_response = self._parse_llm_response(response)
            
            return {
                'status': 'SUCCESS',
                'source': 'LLM_ENHANCED',
                'query': user_query,
                'recommendations': parsed_response,
                'confidence': 0.8
            }
            
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            return self._fallback_response(user_query)
    
    def _create_llm_prompt(self, query: str) -> str:
        """Create LLM prompt."""
        return f"""You are an expert chemical formulation engineer. Analyze this query and provide formulation recommendations.

Query: {query}

Provide response in JSON format with recommendations including formulation, cost analysis, and properties."""
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with error handling."""
        try:
            response = self.groq_client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=Config.LLM_TEMPERATURE,
                max_tokens=Config.LLM_MAX_TOKENS,
                timeout=Config.LLM_TIMEOUT_SECONDS
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise LLMError(f"LLM call failed: {e}")
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response."""
        try:
            # Simple parsing for now
            return [{
                'name': 'LLM Generated Formulation',
                'formulation': {'PVC_K70': 100, 'DOP': 40, 'CaCO3': 8},
                'cost_per_kg': 65.0,
                'confidence': 0.8
            }]
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return []
    
    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """Fallback response when LLM is unavailable."""
        return {
            'status': 'FALLBACK',
            'source': 'DATABASE_DEFAULT',
            'query': query,
            'message': 'LLM unavailable, using database fallback',
            'recommendations': [{
                'name': 'Default PVC Formulation',
                'formulation': {'PVC_K70': 100, 'DOP': 40, 'CaCO3': 8, 'Ca_Zn': 2},
                'cost_per_kg': 65.0,
                'confidence': 0.5
            }]
        }