"""Production LLM interface with robust fallback and error handling."""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from groq import Groq

from .config import Config
from .exceptions import LLMError, ValidationError
from .validators import RequestValidator
from .data_layer import db_manager
from .logging_config import get_logger

logger = get_logger(__name__)


class LLMFormulationAgent:
    """Production LLM agent with intelligent fallback chain."""
    
    def __init__(self):
        """Initialize LLM agent with database and client."""
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
            
            # Initialize entity extractor
            self.entity_extractor = EntityExtractor(
                db_manager.formulations,
                db_manager.ingredients,
                db_manager.suppliers
            )
            
            logger.info("LLM Formulation Agent initialized")
            
        except Exception as e:
            raise LLMError(f"Failed to initialize LLM agent: {e}")
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process user query with intelligent fallback chain."""
        try:
            logger.info(f"Processing query: {user_query[:100]}...")
            
            # Step 1: Try LLM-enhanced processing
            if self.groq_client:
                try:
                    return self._process_with_llm(user_query)
                except LLMError as e:
                    logger.warning(f"LLM processing failed: {e}, falling back to rule-based")
            
            # Step 2: Fall back to rule-based processing
            try:
                return self._process_rule_based(user_query)
            except Exception as e:
                logger.error(f"Rule-based processing failed: {e}, using minimal response")
            
            # Step 3: Minimal response with actual database data
            return self._minimal_response(user_query)
            
        except Exception as e:
            logger.error(f"Query processing completely failed: {e}")
            raise LLMError(f"Failed to process query: {e}")
    
    def _process_with_llm(self, query: str) -> Dict[str, Any]:
        """Process query using LLM with database context."""
        try:
            # Extract entities from query
            entities = self.entity_extractor.extract_query_entities(query)
            
            # Get relevant database context
            context = self._build_database_context(entities)
            
            # Create LLM prompt
            prompt = self._create_llm_prompt(query, context)
            
            # Call LLM with retry logic
            llm_response = self._call_llm_with_retry(prompt)
            
            # Parse and validate LLM response
            parsed_response = self._parse_llm_response(llm_response)
            
            # Enhance with database validation
            enhanced_response = self._enhance_with_database(parsed_response, entities)
            
            return {
                'status': 'SUCCESS',
                'source': 'LLM_ENHANCED',
                'query': query,
                'entities_extracted': entities,
                'recommendations': enhanced_response,
                'confidence': 0.9
            }
            
        except Exception as e:
            raise LLMError(f"LLM processing failed: {e}")
    
    def _process_rule_based(self, query: str) -> Dict[str, Any]:
        """Process query using rule-based system."""
        try:
            # Extract entities
            entities = self.entity_extractor.extract_query_entities(query)
            
            # Convert to structured request
            request = self._entities_to_request(entities, query)
            
            # Validate request
            validated_request = RequestValidator.validate_request(request)
            
            # Find matching formulations
            matches = self._find_database_matches(entities)
            
            # Generate recommendations
            recommendations = self._generate_rule_based_recommendations(matches, validated_request)
            
            return {
                'status': 'SUCCESS',
                'source': 'RULE_BASED',
                'query': query,
                'entities_extracted': entities,
                'validated_request': validated_request,
                'recommendations': recommendations,
                'confidence': 0.7
            }
            
        except Exception as e:
            raise LLMError(f"Rule-based processing failed: {e}")
    
    def _minimal_response(self, query: str) -> Dict[str, Any]:
        """Generate minimal response using database defaults."""
        try:
            # Use first available formulation from database
            formulations = db_manager.formulations
            if not formulations:
                raise LLMError("No formulations available in database")
            
            # Find best default formulation
            default_fm = None
            for fm in formulations:
                if fm.get('compliance_verdict') == 'PASS':
                    default_fm = fm
                    break
            
            if not default_fm:
                default_fm = formulations[0]
            
            # Create minimal recommendation
            recommendation = {
                'name': f"Default Recommendation - {default_fm.get('id', 'Unknown')}",
                'formulation': default_fm.get('formulation', default_fm.get('ingredients', {})),
                'cost_per_kg': default_fm.get('cost_per_kg', 65.0),
                'properties': default_fm.get('properties', {}),
                'compliance': default_fm.get('compliance_verdict', 'UNKNOWN'),
                'confidence': 0.3,
                'rationale': 'Default formulation from database - full analysis unavailable',
                'source_formulation_id': default_fm.get('id', 'Unknown'),
                'risks': 'Limited analysis performed',
                'next_steps': 'Provide more specific requirements for detailed analysis'
            }
            
            return {
                'status': 'DEGRADED_MODE',
                'source': 'DATABASE_DEFAULT',
                'query': query,
                'warning': 'Using default formulation - full analysis unavailable',
                'recommendations': [recommendation],
                'confidence': 0.3
            }
            
        except Exception as e:
            raise LLMError(f"Minimal response generation failed: {e}")
    
    def _build_database_context(self, entities: Dict[str, Any]) -> str:
        """Build relevant database context for LLM."""
        context_parts = []
        
        # Add relevant formulations
        if entities.get('matched_applications'):
            app_formulations = db_manager.formulation_index.find_by_application(
                entities['matched_applications'][0]
            )
            if app_formulations:
                context_parts.append("Relevant formulations:")
                for fm in app_formulations[:3]:
                    context_parts.append(f"- {fm.get('id', 'Unknown')}: {fm.get('formulation', {})}")
        
        # Add cost constraints
        if entities.get('cost_constraints'):
            cost_formulations = db_manager.formulation_index.find_by_cost_range(
                0, entities['cost_constraints']
            )
            if cost_formulations:
                context_parts.append(f"Formulations under ₹{entities['cost_constraints']}/kg:")
                for fm in cost_formulations[:2]:
                    context_parts.append(f"- {fm.get('id', 'Unknown')}: ₹{fm.get('cost_per_kg', 0)}/kg")
        
        # Add supplier information
        if entities.get('matched_materials'):
            for material in entities['matched_materials'][:2]:
                suppliers = db_manager.supplier_index.find_available_suppliers(material)
                if suppliers:
                    supplier = suppliers[0]
                    context_parts.append(f"{material} supplier: {supplier.get('name', 'Unknown')} - ₹{supplier.get('price_per_kg', 0)}/kg")
        
        return "\n".join(context_parts)
    
    def _create_llm_prompt(self, query: str, context: str) -> str:
        """Create structured prompt for LLM."""
        return f"""You are an expert R&D formulation chemist. Analyze this query and provide 3 specific formulation recommendations.

User Query: {query}

Database Context:
{context}

Provide response in this exact JSON format:
{{
  "recommendations": [
    {{
      "name": "Descriptive formulation name",
      "formulation": {{"PVC_K70": 100, "DOP": 40, "CaCO3": 8}},
      "cost_per_kg": 65.5,
      "properties": {{
        "tensile_strength_mpa": 18.2,
        "elongation_percent": 195,
        "hardness_shore": 76
      }},
      "compliance": "PASS",
      "confidence": 0.95,
      "rationale": "Why this formulation was selected based on database evidence",
      "source_formulation_id": "FM-00xx from database",
      "risks": "Any identified risks or limitations",
      "next_steps": "Specific actionable recommendations"
    }}
  ]
}}

CRITICAL: Provide exactly 3 recommendations. Show your reasoning process. Reference database records by ID."""
    
    def _call_llm_with_retry(self, prompt: str) -> str:
        """Call LLM with retry logic and timeout."""
        max_retries = Config.LLM_MAX_RETRIES
        
        for attempt in range(max_retries):
            try:
                response = self.groq_client.chat.completions.create(
                    model=Config.LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=Config.LLM_TEMPERATURE,
                    max_tokens=Config.LLM_MAX_TOKENS,
                    timeout=Config.LLM_TIMEOUT_SECONDS
                )
                
                content = response.choices[0].message.content
                if not content:
                    raise LLMError("Empty response from LLM")
                
                return content
                
            except Exception as e:
                logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise LLMError(f"LLM failed after {max_retries} attempts: {e}")
                
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse and validate LLM JSON response."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise LLMError("No JSON found in LLM response")
            
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            
            recommendations = parsed.get('recommendations', [])
            if not recommendations:
                raise LLMError("No recommendations in LLM response")
            
            # Validate each recommendation
            validated_recommendations = []
            for rec in recommendations:
                if self._validate_recommendation(rec):
                    validated_recommendations.append(rec)
            
            if not validated_recommendations:
                raise LLMError("No valid recommendations in LLM response")
            
            return validated_recommendations
            
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON in LLM response: {e}")
        except Exception as e:
            raise LLMError(f"Failed to parse LLM response: {e}")
    
    def _validate_recommendation(self, rec: Dict[str, Any]) -> bool:
        """Validate individual recommendation structure."""
        required_fields = ['name', 'formulation', 'cost_per_kg', 'confidence']
        
        for field in required_fields:
            if field not in rec:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate formulation structure
        formulation = rec.get('formulation', {})
        if not isinstance(formulation, dict) or not formulation:
            logger.warning("Invalid formulation structure")
            return False
        
        # Validate cost
        cost = rec.get('cost_per_kg', 0)
        if not isinstance(cost, (int, float)) or cost <= 0:
            logger.warning(f"Invalid cost: {cost}")
            return False
        
        return True
    
    def _enhance_with_database(self, recommendations: List[Dict], entities: Dict) -> List[Dict]:
        """Enhance LLM recommendations with database validation."""
        enhanced = []
        
        for rec in recommendations:
            try:
                # Validate materials exist in database
                formulation = rec.get('formulation', {})
                validated_formulation = self._validate_materials(formulation)
                
                # Update with validated formulation
                rec['formulation'] = validated_formulation
                
                # Add supplier information
                rec['supplier_info'] = self._get_supplier_info(validated_formulation)
                
                # Validate cost against suppliers
                rec['cost_validation'] = self._validate_cost(validated_formulation, rec.get('cost_per_kg', 0))
                
                enhanced.append(rec)
                
            except Exception as e:
                logger.warning(f"Failed to enhance recommendation: {e}")
                # Keep original recommendation if enhancement fails
                enhanced.append(rec)
        
        return enhanced
    
    def _validate_materials(self, formulation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate materials exist in database and fix if needed."""
        validated = {}
        
        for material, phr in formulation.items():
            # Check if material exists in suppliers
            suppliers = db_manager.supplier_index.by_product.get(material, [])
            
            if suppliers:
                validated[material] = phr
            else:
                # Try to find similar material
                similar_material = self._find_similar_material(material)
                if similar_material:
                    logger.info(f"Replaced {material} with {similar_material}")
                    validated[similar_material] = phr
                else:
                    logger.warning(f"Material {material} not found in database")
                    validated[material] = phr  # Keep original
        
        return validated
    
    def _find_similar_material(self, material: str) -> Optional[str]:
        """Find similar material in database."""
        available_materials = list(db_manager.supplier_index.by_product.keys())
        
        # Simple similarity matching
        material_lower = material.lower()
        for available in available_materials:
            if material_lower in available.lower() or available.lower() in material_lower:
                return available
        
        return None
    
    def _get_supplier_info(self, formulation: Dict[str, Any]) -> Dict[str, Any]:
        """Get supplier information for formulation materials."""
        supplier_info = {}
        
        for material in formulation.keys():
            suppliers = db_manager.supplier_index.find_available_suppliers(material)
            if suppliers:
                best_supplier = suppliers[0]
                supplier_info[material] = {
                    'supplier': best_supplier.get('name', 'Unknown'),
                    'price_per_kg': best_supplier.get('price_per_kg', 0),
                    'availability': best_supplier.get('availability', 'Unknown')
                }
        
        return supplier_info
    
    def _validate_cost(self, formulation: Dict[str, Any], estimated_cost: float) -> Dict[str, Any]:
        """Validate estimated cost against supplier prices."""
        try:
            # Calculate actual cost from suppliers
            total_cost = 0.0
            total_phr = sum(formulation.values())
            
            for material, phr in formulation.items():
                suppliers = db_manager.supplier_index.find_available_suppliers(material)
                if suppliers:
                    price_per_kg = suppliers[0].get('price_per_kg', 0)
                    weight_fraction = phr / total_phr if total_phr > 0 else 0
                    material_cost = weight_fraction * price_per_kg
                    total_cost += material_cost
            
            # Add processing and overhead
            processing_cost = total_cost * Config.PROCESSING_COST_MULTIPLIER
            overhead_cost = total_cost * Config.OVERHEAD_COST_MULTIPLIER
            actual_cost = total_cost + processing_cost + overhead_cost
            
            cost_difference = abs(estimated_cost - actual_cost)
            cost_accuracy = max(0.0, 1.0 - (cost_difference / max(estimated_cost, actual_cost)))
            
            return {
                'estimated_cost': estimated_cost,
                'calculated_cost': round(actual_cost, 2),
                'difference': round(cost_difference, 2),
                'accuracy': round(cost_accuracy, 2),
                'validation': 'ACCURATE' if cost_accuracy > 0.9 else 'APPROXIMATE'
            }
            
        except Exception as e:
            logger.warning(f"Cost validation failed: {e}")
            return {
                'estimated_cost': estimated_cost,
                'validation': 'UNABLE_TO_VALIDATE',
                'error': str(e)
            }
    
    def _entities_to_request(self, entities: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Convert extracted entities to structured request."""
        request = {
            'application': 'cable_insulation',  # Default
            'cost_limit': Config.DEFAULT_COST_LIMIT,
            'volume_kg': Config.DEFAULT_VOLUME_KG,
            'quality_target': 'IS_5831',
            'delivery_days': Config.DEFAULT_DELIVERY_DAYS
        }
        
        # Update with extracted entities
        if entities.get('matched_applications'):
            request['application'] = entities['matched_applications'][0]
        
        if entities.get('cost_constraints'):
            request['cost_limit'] = entities['cost_constraints']
        
        # Extract volume from query
        import re
        volume_match = re.search(r'(\d+)\s*(?:kg|kilogram)', query.lower())
        if volume_match:
            request['volume_kg'] = int(volume_match.group(1))
        
        return request
    
    def _find_database_matches(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find matching formulations in database."""
        matches = []
        
        # Search by application
        if entities.get('matched_applications'):
            app_matches = db_manager.formulation_index.find_by_application(
                entities['matched_applications'][0]
            )
            matches.extend(app_matches)
        else:
            # If no application match, search for cable insulation
            cable_matches = db_manager.formulation_index.find_by_application('cable_insulation_low_voltage')
            matches.extend(cable_matches)
        
        # Search by cost
        if entities.get('cost_constraints'):
            cost_matches = db_manager.formulation_index.find_by_cost_range(
                0, entities['cost_constraints']
            )
            matches.extend(cost_matches)
        
        # Deduplicate
        seen_ids = set()
        unique_matches = []
        for match in matches:
            match_id = match.get('id', '')
            if match_id and match_id not in seen_ids:
                unique_matches.append(match)
                seen_ids.add(match_id)
        
        return unique_matches[:5]  # Top 5 matches
    
    def _generate_rule_based_recommendations(self, matches: List[Dict], request: Dict) -> List[Dict]:
        """Generate recommendations using rule-based logic."""
        recommendations = []
        
        if not matches:
            # Use default formulation
            default_formulation = {
                'PVC_K70': 100,
                'DOP': 40,
                'CaCO3': 8,
                'Ca_Zn': 2,
                'Additives': 1.5
            }
            
            recommendations.append({
                'name': 'Default PVC Formulation',
                'formulation': default_formulation,
                'cost_per_kg': 65.0,
                'properties': {
                    'tensile_strength_mpa': 18.0,
                    'elongation_percent': 200.0,
                    'hardness_shore': 75.0
                },
                'compliance': 'UNKNOWN',
                'confidence': 0.5,
                'rationale': 'Default formulation - no similar formulations found',
                'source_formulation_id': 'DEFAULT',
                'risks': 'No historical validation',
                'next_steps': 'Validate through testing'
            })
        else:
            # Use database matches
            for i, match in enumerate(matches[:3]):
                formulation = match.get('formula', match.get('formulation', match.get('ingredients', {})))
                properties = match.get('prop', match.get('properties', {}))
                
                recommendations.append({
                    'name': f"Database Match {i+1} - {match.get('id', 'Unknown')}",
                    'formulation': formulation,
                    'cost_per_kg': match.get('cost_per_kg', 65.0),
                    'properties': properties,
                    'compliance': match.get('verdict', match.get('compliance_verdict', 'UNKNOWN')),
                    'confidence': 0.8,
                    'rationale': f"Based on historical formulation {match.get('id', 'Unknown')}",
                    'source_formulation_id': match.get('id', 'Unknown'),
                    'risks': 'Historical formulation - verify current supplier availability',
                    'next_steps': 'Validate material availability and update costs'
                })
        
        return recommendations


class EntityExtractor:
    """Extract entities from user queries for formulation matching."""
    
    def __init__(self, formulations: List[Dict], ingredients: Dict, suppliers: List[Dict]):
        self.formulations = formulations
        self.ingredients = ingredients
        self.suppliers = suppliers
        self._build_entity_index()
    
    def _build_entity_index(self) -> None:
        """Build entity extraction indexes."""
        self.entities = {
            'applications': set(),
            'materials': set(),
            'properties': set(),
            'standards': set(),
            'cost_ranges': [],
            'suppliers': set()
        }
        
        # Extract from formulations
        for fm in self.formulations:
            app = fm.get('app', fm.get('application', ''))
            if app:
                self.entities['applications'].add(app.lower())
            
            formulation = fm.get('formula', fm.get('formulation', fm.get('ingredients', {})))
            if isinstance(formulation, dict):
                for material in formulation.keys():
                    self.entities['materials'].add(material)
            
            if 'cost_per_kg' in fm:
                self.entities['cost_ranges'].append(fm['cost_per_kg'])
        
        # Extract from ingredients
        if isinstance(self.ingredients, dict):
            for category in self.ingredients.values():
                if isinstance(category, list):
                    for item in category:
                        if 'id' in item:
                            self.entities['materials'].add(item['id'])
        
        # Extract from suppliers
        for supplier in self.suppliers:
            product = supplier.get('product', '')
            if product:
                self.entities['materials'].add(product)
            
            name = supplier.get('name', '')
            if name:
                self.entities['suppliers'].add(name)
    
    def extract_query_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from user query."""
        query_lower = query.lower()
        extracted = {
            'matched_applications': [],
            'matched_materials': [],
            'matched_suppliers': [],
            'cost_constraints': None,
            'quality_requirements': []
        }
        
        # Match applications
        for app in self.entities['applications']:
            app_words = app.replace('_', ' ').split()
            if any(word in query_lower for word in app_words):
                extracted['matched_applications'].append(app)
        
        # Match materials
        for material in self.entities['materials']:
            if material.lower() in query_lower:
                extracted['matched_materials'].append(material)
        
        # Extract cost constraints
        import re
        cost_patterns = [
            r'₹\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:rupees?|₹)',
            r'under\s+(\d+)',
            r'below\s+(\d+)',
            r'cost\s+limit\s+(\d+)'
        ]
        
        for pattern in cost_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                extracted['cost_constraints'] = float(matches[0])
                break
        
        # Match suppliers
        for supplier in self.entities['suppliers']:
            if supplier.lower() in query_lower:
                extracted['matched_suppliers'].append(supplier)
        
        return extracted