import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from src.llm_interface import LLMFormulationAgent
from src.rd_agent_core import RDAgent
from src.config import Config
from src.logging_config import get_logger

logger = get_logger(__name__)


class FormulationApp:
    def __init__(self):
        try:
            # Validate configuration
            Config.validate()
            logger.info("Configuration validated")
            
            # Initialize agents
            self.llm_agent = LLMFormulationAgent()
            self.ml_agent = RDAgent()
            
            logger.info("✓ Production RND Agent System initialized")
            print("✓ Production RND Agent System ready")
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            print(f"✗ System initialization failed: {e}")
            raise
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        logger.info(f"Processing query: {user_query}")
        print(f"\n🔍 Processing: {user_query}")
        print("-" * 60)
        
        try:
            # Step 1: Try LLM Agent first
            result = self.llm_agent.process_query(user_query)
            print(f"✓ {result.get('source', 'LLM')} response generated")
            return result
            
        except Exception as e:
            logger.warning(f"LLM processing failed: {e}, trying ML agent")
            print(f"⚠ LLM processing failed, trying ML agent...")
            
            # Step 2: Try ML Agent
            try:
                request = self._parse_query_to_request(user_query)
                result = self.ml_agent.design_formulation(request)
                print("✓ ML Agent response generated")
                return result
                
            except Exception as e2:
                logger.error(f"Both agents failed: LLM={e}, ML={e2}")
                print(f"✗ All systems failed")
                return self._emergency_response(user_query, str(e), str(e2))
    
    def _parse_query_to_request(self, query: str) -> Dict[str, Any]:
        """Parse natural language query to structured request."""
        import re
        
        # Extract cost constraint
        cost_match = re.search(r'₹?(\d+(?:\.\d+)?)\s*(?:/kg|per\s*kg)', query.lower())
        cost_limit = float(cost_match.group(1)) if cost_match else Config.DEFAULT_COST_LIMIT
        
        # Extract volume
        volume_match = re.search(r'(\d+)\s*(?:kg|kilogram)', query.lower())
        volume_kg = int(volume_match.group(1)) if volume_match else Config.DEFAULT_VOLUME_KG
        
        # Map application keywords
        app_keywords = {
            'cable': 'cable_insulation_low_voltage',
            'insulation': 'cable_insulation_low_voltage', 
            'pipe': 'pvc_pipe_compound',
            'film': 'pvc_film_grade',
            'wire': 'cable_insulation_low_voltage'
        }
        
        application = 'general_compound'
        for keyword, app_name in app_keywords.items():
            if keyword in query.lower():
                application = app_name
                break
        
        return {
            'application': application,
            'cost_limit': cost_limit,
            'volume_kg': volume_kg,
            'quality_target': 'IS_5831',
            'delivery_days': Config.DEFAULT_DELIVERY_DAYS
        }
    
    def _emergency_response(self, query: str, llm_error: str = "", ml_error: str = "") -> Dict[str, Any]:
        """Emergency fallback response."""
        return {
            "status": "SYSTEM_UNAVAILABLE",
            "message": "All formulation systems are currently unavailable",
            "query": query,
            "errors": {
                "llm_error": llm_error,
                "ml_error": ml_error
            },
            "contact": "Check logs for details or contact technical support"
        }


def main():
    """Main entry point for production system."""
    try:
        # Initialize system
        app = FormulationApp()
        
        # Interactive mode
        print("\n" + "="*60)
        print("🧪 PRODUCTION RND AGENT SYSTEM")
        print("="*60)
        print("Enter formulation queries (type 'quit' to exit)")
        print("Example: 'PVC cable insulation under ₹65/kg for 500kg'")
        print("-"*60)
        
        while True:
            try:
                query = input("\n📝 Query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                # Process query
                result = app.process_query(query)
                
                # Display results
                print("\n📊 RESULTS:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Query processing error: {e}")
                print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ System startup failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())