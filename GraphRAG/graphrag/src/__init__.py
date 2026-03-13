"""GraphRAG Agent System - Production-ready chemical formulation intelligence."""

__version__ = "1.0.0"
__author__ = "R&D Agent Team"
__description__ = "GraphRAG-enhanced chemical formulation system"

from .graphrag_agent import graphrag_agent
from .config import Config
from .exceptions import *

__all__ = [
    'graphrag_agent',
    'Config',
    'GraphRAGError',
    'FormulationError',
    'SemanticSearchError',
    'KnowledgeGraphError'
]