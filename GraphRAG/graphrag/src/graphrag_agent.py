"""Production GraphRAG Agent with complete semantic reasoning and graph traversal."""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from knowledge_graph import GraphRAGEngine
from config import Config
from exceptions import GraphRAGError, FormulationError, ExceptionHandler
from logging_config import get_logger, RequestLogger, PerformanceLogger
from formulation_validators import RequestValidator, PropertyValidator
from data_layer import db_manager

logger = get_logger(__name__)
perf_logger = PerformanceLogger(__name__)
request_logger = RequestLogger(__name__)


@dataclass
class GraphRAGRecommendation:
    """Complete GraphRAG recommendation with all analysis."""
    
    formulation_id: str
    name: str
    formulation: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    properties: Dict[str, Any]
    compliance: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    semantic_score: float
    graph_score: float
    combined_score: float
    confidence: float
    reasoning_path: List[str]
    materials_info: List[Dict[str, Any]]
    suppliers_info: Dict[str, List[Dict[str, Any]]]
    next_steps: List[str]


class SemanticQueryAnalyzer:
    """Advanced semantic query analysis for chemical formulation requests."""
    
    def __init__(self):
        self.intent_patterns = {
            'cost_optimization': ['cheap', 'budget', 'low cost', 'economical', 'affordable'],
            'quality_focus': ['premium', 'high quality', 'superior', 'best', 'excellent'],
            'eco_friendly': ['eco', 'green', 'sustainable', 'environmental', 'phthalate free'],
            'fast_processing': ['quick', 'fast', 'rapid', 'speed', 'urgent'],
            'compliance_critical': ['standard', 'compliance', 'regulation', 'certified', 'approved']
        }
        
        self.application_keywords = {
            'cable_insulation_low_voltage': ['cable', 'wire', 'insulation', 'electrical', '1100v', 'low voltage'],
            'pvc_pipe_compound': ['pipe', 'plumbing', 'water', 'pressure', 'drainage'],
            'pvc_film_grade': ['film', 'sheet', 'packaging', 'flexible'],
            'pvc_profile_compound': ['profile', 'window', 'door', 'construction', 'rigid']
        }
        
        self.property_keywords = {
            'tensile_strength': ['strong', 'strength', 'tough', 'durable', 'robust'],
            'elongation': ['flexible', 'stretch', 'elongation', 'bend', 'elastic'],
            'hardness': ['hard', 'rigid', 'stiff', 'firm'],
            'brittleness_temp': ['cold', 'winter', 'low temperature', 'brittle']
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Comprehensive query analysis with intent extraction."""
        query_lower = query.lower()
        
        analysis = {
            'primary_intent': self._extract_primary_intent(query_lower),
            'applications': self._extract_applications(query_lower),
            'property_requirements': self._extract_property_requirements(query_lower),
            'cost_constraints': self._extract_cost_constraints(query_lower),
            'volume_requirements': self._extract_volume_requirements(query_lower),
            'quality_standards': self._extract_quality_standards(query_lower),
            'material_preferences': self._extract_material_preferences(query_lower),
            'urgency_level': self._extract_urgency_level(query_lower),
            'semantic_concepts': self._extract_semantic_concepts(query_lower)
        }
        
        return analysis
    
    def _extract_primary_intent(self, query: str) -> str:
        """Extract primary intent from query."""
        intent_scores = {}
        
        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in query)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return 'general_formulation'
    
    def _extract_applications(self, query: str) -> List[str]:
        """Extract application types from query."""
        applications = []
        
        for app, keywords in self.application_keywords.items():
            if any(keyword in query for keyword in keywords):
                applications.append(app)
        
        return applications if applications else ['general_compound']
    
    def _extract_property_requirements(self, query: str) -> List[str]:
        """Extract property requirements from query."""
        properties = []
        
        for prop, keywords in self.property_keywords.items():
            if any(keyword in query for keyword in keywords):
                properties.append(prop)
        
        return properties
    
    def _extract_cost_constraints(self, query: str) -> Optional[float]:
        """Extract cost constraints from query."""
        import re
        
        patterns = [
            r'₹\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:rupees?|₹)',
            r'under\s+(\d+)',
            r'below\s+(\d+)',
            r'maximum\s+(\d+)',
            r'limit\s+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_volume_requirements(self, query: str) -> Optional[int]:
        """Extract volume requirements from query."""
        import re
        
        patterns = [
            r'(\d+)\s*(?:kg|kilogram)',
            r'(\d+)\s*(?:ton|tonne)',
            r'batch\s+of\s+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                value = int(match.group(1))
                if 'ton' in pattern:
                    value *= 1000  # Convert tons to kg
                return value
        
        return None
    
    def _extract_quality_standards(self, query: str) -> List[str]:
        """Extract quality standards from query."""
        standards = []
        
        standard_patterns = [
            r'IS[_\s]?(\d+)',
            r'ASTM[_\s]?([A-Z]\d+)',
            r'RoHS',
            r'REACH'
        ]
        
        for pattern in standard_patterns:
            import re
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    standards.append(f"IS_{match[0]}" if 'IS' in pattern else f"ASTM_{match[0]}")
                else:
                    standards.append(match.upper())
        
        return standards if standards else ['IS_5831']  # Default standard
    
    def _extract_material_preferences(self, query: str) -> Dict[str, List[str]]:
        """Extract material preferences (preferred/avoided)."""
        preferences = {'preferred': [], 'avoided': []}
        
        # Common materials
        materials = ['PVC', 'DOP', 'DBP', 'DOTP', 'DINP', 'CaCO3', 'TiO2', 'Ca_Zn', 'Ba_Zn']
        
        for material in materials:
            if material.lower() in query:
                if any(word in query for word in ['avoid', 'without', 'exclude', 'no']):
                    preferences['avoided'].append(material)
                else:
                    preferences['preferred'].append(material)
        
        return preferences
    
    def _extract_urgency_level(self, query: str) -> str:
        """Extract urgency level from query."""
        urgent_keywords = ['urgent', 'asap', 'immediate', 'rush', 'emergency']
        normal_keywords = ['standard', 'normal', 'regular']
        
        if any(keyword in query for keyword in urgent_keywords):
            return 'high'
        elif any(keyword in query for keyword in normal_keywords):
            return 'normal'
        else:
            return 'medium'
    
    def _extract_semantic_concepts(self, query: str) -> List[str]:
        """Extract high-level semantic concepts."""
        concepts = []
        
        concept_patterns = {
            'innovation': ['innovative', 'novel', 'new', 'advanced', 'cutting-edge'],
            'reliability': ['reliable', 'proven', 'tested', 'stable', 'consistent'],
            'performance': ['performance', 'efficiency', 'optimization', 'enhanced'],
            'sustainability': ['sustainable', 'recyclable', 'biodegradable', 'circular'],
            'scalability': ['scalable', 'production', 'manufacturing', 'industrial']
        }
        
        for concept, keywords in concept_patterns.items():
            if any(keyword in query for keyword in keywords):
                concepts.append(concept)
        
        return concepts


class GraphRAGFormulationAgent:
    """Production GraphRAG agent with complete formulation intelligence."""
    
    def __init__(self, graphrag_engine: Optional[GraphRAGEngine] = None):
        """Initialize GraphRAG formulation agent."""
        try:
            # Initialize components
            self.graphrag_engine = graphrag_engine or GraphRAGEngine()
            self.query_analyzer = SemanticQueryAnalyzer()
            
            # Initialize database
            db_manager.initialize()
            
            # Performance tracking
            self.query_count = 0
            self.total_processing_time = 0.0
            
            logger.info("GraphRAG Formulation Agent initialized successfully")
            
        except Exception as e:
            raise GraphRAGError(f"Failed to initialize GraphRAG agent: {e}")
    
    @ExceptionHandler.handle_exceptions
    @request_logger.log_request
    def enhanced_formulation_design(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Complete enhanced formulation design using GraphRAG intelligence."""
        start_time = time.time()
        
        try:
            with perf_logger.timer("enhanced_formulation_design"):
                logger.info(f"Starting enhanced formulation design: {request}")
                
                # Step 1: Validate and enhance request
                validated_request = self._validate_and_enhance_request(request)
                
                # Step 2: Semantic query analysis
                query = self._construct_semantic_query(validated_request)
                query_analysis = self.query_analyzer.analyze_query(query)
                
                # Step 3: GraphRAG path search
                graph_results = self.graphrag_engine.find_formulation_paths(
                    query, constraints=validated_request
                )
                
                # Step 4: Enhanced recommendation generation
                recommendations = self._generate_enhanced_recommendations(
                    graph_results, validated_request, query_analysis
                )
                
                # Step 5: Risk assessment and validation
                validated_recommendations = self._validate_recommendations(
                    recommendations, validated_request
                )
                
                # Step 6: Generate insights and explanations
                insights = self._generate_formulation_insights(
                    validated_recommendations, query_analysis
                )
                
                # Step 7: Compile final response
                processing_time = time.time() - start_time
                self._update_performance_metrics(processing_time)
                
                response = {
                    'status': 'COMPLETE',
                    'source': 'GRAPHRAG_ENHANCED',
                    'request_id': f"GRAG-{hash(str(validated_request)) % 10000:04d}",
                    'processing_time_seconds': round(processing_time, 2),
                    'validated_request': validated_request,
                    'query_analysis': query_analysis,
                    'semantic_query': query,
                    'graph_matches_found': len(graph_results),
                    'top_5_recommendations': validated_recommendations[:5],
                    'confidence_score': self._calculate_overall_confidence(validated_recommendations),
                    'formulation_insights': insights,
                    'next_steps': self._generate_next_steps(validated_recommendations, validated_request),
                    'graph_statistics': self.graphrag_engine.get_graph_statistics()
                }
                
                logger.info(f"Enhanced formulation design completed: {len(validated_recommendations)} recommendations")
                return response
                
        except Exception as e:
            logger.error(f"Enhanced formulation design failed: {e}")
            raise FormulationError(f"GraphRAG formulation design failed: {e}")
    
    def _validate_and_enhance_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance request with defaults and corrections."""
        try:
            # Basic validation
            validated = RequestValidator.validate_request(request)
            
            # Enhance with intelligent defaults
            if not validated.get('application'):
                validated['application'] = 'cable_insulation_low_voltage'
            
            if not validated.get('cost_limit'):
                validated['cost_limit'] = Config.DEFAULT_COST_LIMIT
            
            if not validated.get('volume_kg'):
                validated['volume_kg'] = Config.DEFAULT_VOLUME_KG
            
            if not validated.get('quality_target'):
                validated['quality_target'] = 'IS_5831'
            
            if not validated.get('delivery_days'):
                validated['delivery_days'] = Config.DEFAULT_DELIVERY_DAYS
            
            # Add GraphRAG-specific enhancements
            validated['semantic_preferences'] = request.get('semantic_preferences', {})
            validated['innovation_level'] = request.get('innovation_level', 'balanced')
            validated['sustainability_focus'] = request.get('sustainability_focus', False)
            
            return validated
            
        except Exception as e:
            raise FormulationError(f"Request validation failed: {e}")
    
    def _construct_semantic_query(self, request: Dict[str, Any]) -> str:
        """Construct semantic query from structured request."""
        query_parts = []
        
        # Application
        app = request.get('application', '')
        if app:
            app_readable = app.replace('_', ' ')
            query_parts.append(app_readable)
        
        # Cost constraint
        cost_limit = request.get('cost_limit', 0)
        if cost_limit > 0:
            query_parts.append(f"cost under ₹{cost_limit} per kg")
        
        # Volume
        volume = request.get('volume_kg', 0)
        if volume > 0:
            query_parts.append(f"batch size {volume} kg")
        
        # Quality target
        quality = request.get('quality_target', '')
        if quality:
            query_parts.append(f"meeting {quality} standard")
        
        # Semantic preferences
        preferences = request.get('semantic_preferences', {})
        if preferences.get('eco_friendly'):
            query_parts.append("environmentally friendly")
        if preferences.get('high_performance'):
            query_parts.append("high performance")
        if preferences.get('cost_optimized'):
            query_parts.append("cost optimized")
        
        # Innovation level
        innovation = request.get('innovation_level', 'balanced')
        if innovation == 'high':
            query_parts.append("innovative advanced formulation")
        elif innovation == 'conservative':
            query_parts.append("proven reliable formulation")
        
        return ' '.join(query_parts)
    
    def _generate_enhanced_recommendations(self, graph_results: List[Dict[str, Any]], 
                                         request: Dict[str, Any], 
                                         query_analysis: Dict[str, Any]) -> List[GraphRAGRecommendation]:
        """Generate enhanced recommendations with complete analysis."""
        recommendations = []
        
        for i, result in enumerate(graph_results):
            try:
                # Extract formulation data
                fm_data = result['formulation_data']
                materials = result.get('materials', [])
                suppliers = result.get('suppliers', {})
                
                # Generate comprehensive analysis
                cost_analysis = self._analyze_formulation_cost(fm_data, materials, suppliers, request)
                properties = self._predict_formulation_properties(fm_data, materials)
                compliance = self._check_formulation_compliance(properties, request)
                risk_assessment = self._assess_formulation_risks(fm_data, cost_analysis, suppliers, request)
                
                # Generate reasoning path
                reasoning_path = self._generate_reasoning_path(
                    result, query_analysis, cost_analysis, compliance, risk_assessment
                )
                
                # Calculate enhanced scores
                enhanced_scores = self._calculate_enhanced_scores(
                    result, cost_analysis, properties, compliance, risk_assessment, request, query_analysis
                )
                
                # Generate next steps
                next_steps = self._generate_recommendation_next_steps(
                    fm_data, cost_analysis, compliance, risk_assessment
                )
                
                recommendation = GraphRAGRecommendation(
                    formulation_id=result['formulation_id'],
                    name=f"GraphRAG Recommendation {i+1} - {result['formulation_id']}",
                    formulation=fm_data.get('formula', fm_data.get('formulation', {})),
                    cost_analysis=cost_analysis,
                    properties=properties,
                    compliance=compliance,
                    risk_assessment=risk_assessment,
                    semantic_score=result.get('semantic_score', 0.5),
                    graph_score=result.get('graph_weight', 0.5),
                    combined_score=enhanced_scores['combined_score'],
                    confidence=enhanced_scores['confidence'],
                    reasoning_path=reasoning_path,
                    materials_info=materials,
                    suppliers_info=suppliers,
                    next_steps=next_steps
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.warning(f"Failed to generate recommendation for {result.get('formulation_id', 'unknown')}: {e}")
                continue
        
        # Sort by combined score
        recommendations.sort(key=lambda x: x.combined_score, reverse=True)
        return recommendations
    
    def _analyze_formulation_cost(self, fm_data: Dict[str, Any], materials: List[Dict[str, Any]], 
                                suppliers: Dict[str, List[Dict[str, Any]]], request: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive cost analysis using GraphRAG supplier data."""
        try:
            volume_kg = request.get('volume_kg', 100)
            
            # Calculate material costs using GraphRAG supplier data
            material_costs = {}
            total_material_cost = 0.0
            supplier_risks = []
            
            formulation = fm_data.get('formula', fm_data.get('formulation', {}))
            total_phr = sum(
                data.get('phr', data) if isinstance(data, dict) else data 
                for data in formulation.values()
            )
            
            for material_name, phr_data in formulation.items():
                phr = phr_data.get('phr', phr_data) if isinstance(phr_data, dict) else phr_data
                
                # Find best supplier from GraphRAG data
                material_suppliers = suppliers.get(material_name, [])
                
                if material_suppliers:
                    # Sort by reliability and price
                    best_supplier = min(material_suppliers, 
                                      key=lambda s: (s.get('price_per_kg', 999), -s.get('reliability', 0)))
                    
                    price_per_kg = best_supplier.get('price_per_kg', 0)
                    availability = best_supplier.get('availability', 'Unknown')
                    
                    if availability != 'Yes':
                        supplier_risks.append(f"{material_name}: {availability} availability")
                else:
                    # Fallback to database lookup
                    price_per_kg = self._get_fallback_material_cost(material_name)
                    supplier_risks.append(f"{material_name}: No GraphRAG supplier data")
                
                # Calculate cost for this material
                weight_fraction = phr / total_phr if total_phr > 0 else 0
                material_weight = volume_kg * weight_fraction
                material_cost = material_weight * price_per_kg
                
                material_costs[material_name] = {
                    'phr': phr,
                    'weight_kg': round(material_weight, 2),
                    'price_per_kg': price_per_kg,
                    'total_cost': round(material_cost, 2),
                    'supplier_info': material_suppliers[0] if material_suppliers else None
                }
                
                total_material_cost += material_cost
            
            # Calculate processing and overhead costs
            processing_cost = total_material_cost * Config.PROCESSING_COST_MULTIPLIER
            overhead_cost = total_material_cost * Config.OVERHEAD_COST_MULTIPLIER
            
            total_cost = total_material_cost + processing_cost + overhead_cost
            cost_per_kg = total_cost / volume_kg if volume_kg > 0 else 0
            
            return {
                'material_costs': material_costs,
                'total_material_cost': round(total_material_cost, 2),
                'processing_cost': round(processing_cost, 2),
                'overhead_cost': round(overhead_cost, 2),
                'total_production_cost': round(total_cost, 2),
                'total_cost_per_kg': round(cost_per_kg, 2),
                'volume_kg': volume_kg,
                'supplier_risks': supplier_risks,
                'cost_breakdown_percentage': {
                    'materials': round((total_material_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
                    'processing': round((processing_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
                    'overhead': round((overhead_cost / total_cost) * 100, 1) if total_cost > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Cost analysis failed: {e}")
            return {
                'total_cost_per_kg': fm_data.get('cost_per_kg', 65.0),
                'error': str(e)
            }
    
    def _predict_formulation_properties(self, fm_data: Dict[str, Any], materials: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict formulation properties using GraphRAG material data."""
        try:
            # Use existing properties if available
            existing_props = fm_data.get('prop', fm_data.get('properties', {}))
            if existing_props:
                return self._normalize_property_names(existing_props)
            
            # Predict properties using material composition
            formulation = fm_data.get('formula', fm_data.get('formulation', {}))
            
            # Simple property prediction based on material composition
            predicted_props = {
                'tensile_strength_mpa': 18.0,  # Base value
                'elongation_percent': 200.0,
                'hardness_shore': 75.0,
                'brittleness_temp_c': -25.0,
                'viscosity_cps': 800.0
            }
            
            # Adjust based on material composition
            for material_name, phr_data in formulation.items():
                phr = phr_data.get('phr', phr_data) if isinstance(phr_data, dict) else phr_data
                
                # Apply material-specific adjustments
                if 'PVC_K72' in material_name:
                    predicted_props['tensile_strength_mpa'] += 2.0
                    predicted_props['hardness_shore'] += 3.0
                elif 'DOP' in material_name:
                    predicted_props['elongation_percent'] += phr * 2.0
                    predicted_props['hardness_shore'] -= phr * 0.3
                elif 'CaCO3' in material_name:
                    predicted_props['hardness_shore'] += phr * 0.5
                    predicted_props['tensile_strength_mpa'] -= phr * 0.1
            
            # Ensure realistic ranges
            predicted_props['tensile_strength_mpa'] = max(10.0, min(30.0, predicted_props['tensile_strength_mpa']))
            predicted_props['elongation_percent'] = max(100.0, min(400.0, predicted_props['elongation_percent']))
            predicted_props['hardness_shore'] = max(40.0, min(95.0, predicted_props['hardness_shore']))
            
            return predicted_props
            
        except Exception as e:
            logger.error(f"Property prediction failed: {e}")
            return {
                'tensile_strength_mpa': 18.0,
                'elongation_percent': 200.0,
                'hardness_shore': 75.0,
                'error': str(e)
            }
    
    def _check_formulation_compliance(self, properties: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        """Check formulation compliance against standards."""
        try:
            standard = request.get('quality_target', 'IS_5831')
            standards = db_manager.standards
            
            if standard not in standards:
                return {
                    'verdict': 'UNKNOWN',
                    'standard': standard,
                    'message': f"Standard {standard} not found in database",
                    'confidence': 0.0
                }
            
            std_requirements = standards[standard]
            compliance_details = []
            passed_tests = 0
            total_tests = 0
            
            # Property mapping
            prop_mapping = {
                'tensile_strength_mpa': 'tensile_strength',
                'elongation_percent': 'elongation',
                'hardness_shore': 'hardness',
                'brittleness_temp_c': 'brittleness_temp'
            }
            
            for prop_key, prop_value in properties.items():
                if prop_key in prop_mapping and isinstance(prop_value, (int, float)):
                    std_prop = prop_mapping[prop_key]
                    
                    if std_prop in std_requirements:
                        requirement = std_requirements[std_prop]
                        min_val = requirement.get('min', float('-inf'))
                        max_val = requirement.get('max', float('inf'))
                        
                        total_tests += 1
                        
                        if min_val <= prop_value <= max_val:
                            passed_tests += 1
                            status = 'PASS'
                        else:
                            status = 'FAIL'
                        
                        compliance_details.append({
                            'property': prop_key,
                            'value': prop_value,
                            'requirement': f"{min_val} - {max_val}",
                            'status': status
                        })
            
            # Calculate overall verdict
            if total_tests == 0:
                verdict = 'UNKNOWN'
                confidence = 0.0
            else:
                pass_rate = passed_tests / total_tests
                verdict = 'PASS' if pass_rate >= 0.8 else 'FAIL'
                confidence = pass_rate
            
            return {
                'verdict': verdict,
                'standard': standard,
                'passed_tests': passed_tests,
                'total_tests': total_tests,
                'pass_rate': round(confidence, 2),
                'confidence': round(confidence, 2),
                'details': compliance_details
            }
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {
                'verdict': 'ERROR',
                'standard': request.get('quality_target', 'Unknown'),
                'error': str(e),
                'confidence': 0.0
            }
    
    def _assess_formulation_risks(self, fm_data: Dict[str, Any], cost_analysis: Dict[str, Any], 
                                suppliers: Dict[str, List[Dict[str, Any]]], request: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive risk assessment using GraphRAG data."""
        try:
            risks = []
            risk_scores = {}
            
            # Cost risk
            cost_per_kg = cost_analysis.get('total_cost_per_kg', 0)
            cost_limit = request.get('cost_limit', 70.0)
            
            if cost_per_kg > cost_limit:
                cost_risk = min(1.0, (cost_per_kg - cost_limit) / cost_limit)
                risks.append(f"Cost exceeds limit: ₹{cost_per_kg}/kg > ₹{cost_limit}/kg")
            else:
                cost_risk = max(0.0, 1.0 - (cost_limit - cost_per_kg) / cost_limit)
            
            risk_scores['cost_risk'] = cost_risk
            
            # Supplier risk
            supplier_risks = cost_analysis.get('supplier_risks', [])
            supplier_risk = len(supplier_risks) * 0.2
            risk_scores['supplier_risk'] = min(1.0, supplier_risk)
            
            if supplier_risks:
                risks.extend(supplier_risks)
            
            # Material availability risk
            availability_risk = 0.0
            for material_name, material_suppliers in suppliers.items():
                if not material_suppliers:
                    availability_risk += 0.3
                    risks.append(f"{material_name}: No reliable suppliers found")
                else:
                    best_supplier = material_suppliers[0]
                    if best_supplier.get('availability', 'Unknown') != 'Yes':
                        availability_risk += 0.1
            
            risk_scores['availability_risk'] = min(1.0, availability_risk)
            
            # Complexity risk
            formulation = fm_data.get('formula', fm_data.get('formulation', {}))
            complexity_risk = max(0.0, (len(formulation) - 5) * 0.1)
            risk_scores['complexity_risk'] = min(1.0, complexity_risk)
            
            if len(formulation) > 8:
                risks.append(f"Complex formulation: {len(formulation)} ingredients")
            
            # Quality risk
            compliance_verdict = fm_data.get('verdict', fm_data.get('compliance_verdict', 'UNKNOWN'))
            quality_risk = {
                'PASS': 0.1,
                'BORDERLINE': 0.4,
                'FAIL': 0.8,
                'UNKNOWN': 0.5
            }.get(compliance_verdict, 0.5)
            
            risk_scores['quality_risk'] = quality_risk
            
            if compliance_verdict in ['FAIL', 'BORDERLINE']:
                risks.append(f"Quality concern: {compliance_verdict} compliance")
            
            # Calculate overall risk
            overall_risk = sum(risk_scores.values()) / len(risk_scores)
            
            # Risk level classification
            if overall_risk < 0.3:
                risk_level = 'LOW'
            elif overall_risk < 0.6:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'HIGH'
            
            # Success probability
            success_probability = max(0.1, 1.0 - overall_risk)
            
            return {
                'overall_risk_score': round(overall_risk, 2),
                'risk_level': risk_level,
                'success_probability': round(success_probability, 2),
                'identified_risks': risks,
                'risk_breakdown': risk_scores,
                'mitigation_suggestions': self._generate_risk_mitigation(risks, risk_scores)
            }
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return {
                'overall_risk_score': 0.5,
                'risk_level': 'MEDIUM',
                'success_probability': 0.5,
                'error': str(e)
            }
    
    def _generate_reasoning_path(self, result: Dict[str, Any], query_analysis: Dict[str, Any], 
                               cost_analysis: Dict[str, Any], compliance: Dict[str, Any], 
                               risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate detailed reasoning path for recommendation."""
        reasoning = []
        
        # Semantic matching
        semantic_score = result.get('semantic_score', 0)
        if semantic_score > 0.7:
            reasoning.append(f"Strong semantic match (score: {semantic_score:.2f}) to query requirements")
        elif semantic_score > 0.4:
            reasoning.append(f"Good semantic relevance (score: {semantic_score:.2f}) to query")
        else:
            reasoning.append(f"Moderate semantic match (score: {semantic_score:.2f})")
        
        # Graph relevance
        graph_score = result.get('graph_weight', 0)
        if graph_score > 0.8:
            reasoning.append("High graph connectivity indicates proven material combinations")
        elif graph_score > 0.5:
            reasoning.append("Good graph connectivity suggests reliable formulation")
        
        # Cost analysis
        cost_per_kg = cost_analysis.get('total_cost_per_kg', 0)
        if cost_per_kg > 0:
            reasoning.append(f"Cost analysis: ₹{cost_per_kg}/kg production cost")
        
        # Compliance status
        compliance_verdict = compliance.get('verdict', 'UNKNOWN')
        if compliance_verdict == 'PASS':
            reasoning.append(f"Meets {compliance.get('standard', 'quality')} compliance requirements")
        elif compliance_verdict == 'FAIL':
            reasoning.append(f"Does not meet {compliance.get('standard', 'quality')} requirements")
        else:
            reasoning.append(f"Compliance status: {compliance_verdict}")
        
        # Risk factors
        risk_level = risk_assessment.get('risk_level', 'MEDIUM')
        success_prob = risk_assessment.get('success_probability', 0.5)
        reasoning.append(f"Risk assessment: {risk_level} risk, {success_prob:.0%} success probability")
        
        # Intent alignment
        primary_intent = query_analysis.get('primary_intent', 'general_formulation')
        if primary_intent == 'cost_optimization' and cost_per_kg > 0:
            reasoning.append("Aligned with cost optimization intent")
        elif primary_intent == 'quality_focus':
            reasoning.append("Focused on quality performance")
        elif primary_intent == 'eco_friendly':
            reasoning.append("Considers environmental impact")
        
        return reasoning
    
    def _calculate_enhanced_scores(self, result: Dict[str, Any], cost_analysis: Dict[str, Any], 
                                 properties: Dict[str, Any], compliance: Dict[str, Any], risk_assessment: Dict[str, Any], 
                                 request: Dict[str, Any], query_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate enhanced scoring with multiple factors."""
        scores = {}
        
        # Base scores from GraphRAG
        semantic_score = result.get('semantic_score', 0.5)
        graph_score = result.get('graph_weight', 0.5)
        
        # Cost score (30% weight)
        cost_per_kg = cost_analysis.get('total_cost_per_kg', 0)
        cost_limit = request.get('cost_limit', 70.0)
        
        if cost_per_kg <= cost_limit:
            cost_score = (cost_limit - cost_per_kg) / cost_limit
        else:
            cost_score = max(0.0, 1.0 - (cost_per_kg - cost_limit) / cost_limit)
        
        scores['cost_score'] = cost_score
        
        # Compliance score (25% weight)
        compliance_score = compliance.get('confidence', 0.5)
        if compliance.get('verdict') == 'PASS':
            compliance_score += 0.2  # Bonus for passing
        
        scores['compliance_score'] = min(1.0, compliance_score)
        
        # Risk score (15% weight) - inverted (lower risk = higher score)
        risk_score = 1.0 - risk_assessment.get('overall_risk_score', 0.5)
        scores['risk_score'] = risk_score
        
        # Intent alignment score (10% weight)
        intent_score = self._calculate_intent_alignment_score(result, query_analysis)
        scores['intent_score'] = intent_score
        
        # Calculate combined score
        combined_score = (
            semantic_score * 0.20 +
            graph_score * 0.20 +
            cost_score * 0.30 +
            compliance_score * 0.25 +
            risk_score * 0.15 +
            intent_score * 0.10
        )
        
        scores['combined_score'] = round(max(0.0, min(1.0, combined_score)), 3)
        
        # Calculate confidence based on multiple factors
        confidence_factors = []
        
        # Semantic relevance factor
        if semantic_score > 0.7:
            confidence_factors.append(0.9)
        elif semantic_score > 0.5:
            confidence_factors.append(0.7)
        elif semantic_score > 0.3:
            confidence_factors.append(0.5)
        else:
            confidence_factors.append(0.3)
        
        # Graph connectivity factor
        if graph_score > 0.6:
            confidence_factors.append(0.8)
        elif graph_score > 0.4:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.4)
        
        # Cost feasibility factor
        if cost_score > 0.8:
            confidence_factors.append(0.9)
        elif cost_score > 0.6:
            confidence_factors.append(0.7)
        elif cost_score > 0.4:
            confidence_factors.append(0.5)
        else:
            confidence_factors.append(0.3)
        
        # Compliance factor
        if compliance.get('verdict') == 'PASS':
            confidence_factors.append(0.8)
        elif compliance.get('verdict') == 'PARTIAL':
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.4)
        
        # Data completeness factor
        fm_data = result.get('formulation_data', {})
        completeness_score = 0.0
        if fm_data.get('formulation'):
            completeness_score += 0.3
        if cost_analysis.get('total_cost_per_kg', 0) > 0:
            completeness_score += 0.3
        if properties.get('tensile_strength'):
            completeness_score += 0.2
        if len(result.get('materials', [])) > 0:
            completeness_score += 0.2
        
        confidence_factors.append(completeness_score)
        
        # Calculate weighted confidence
        confidence = sum(confidence_factors) / len(confidence_factors)
        
        # Apply bonus for high combined score
        if combined_score > 0.7:
            confidence = min(1.0, confidence + 0.1)
        elif combined_score > 0.5:
            confidence = min(1.0, confidence + 0.05)
        
        scores['confidence'] = round(confidence, 2)
        
        return scores
    
    def _calculate_intent_alignment_score(self, result: Dict[str, Any], query_analysis: Dict[str, Any]) -> float:
        """Calculate how well the formulation aligns with user intent."""
        alignment_score = 0.0
        
        primary_intent = query_analysis.get('primary_intent', 'general_formulation')
        fm_data = result.get('formulation_data', {})
        
        # Cost optimization intent
        if primary_intent == 'cost_optimization':
            cost = fm_data.get('cost_per_kg', 65.0)
            if cost < 60.0:
                alignment_score += 0.4
            elif cost < 70.0:
                alignment_score += 0.2
        
        # Quality focus intent
        elif primary_intent == 'quality_focus':
            verdict = fm_data.get('verdict', fm_data.get('compliance_verdict', 'UNKNOWN'))
            if verdict == 'PASS':
                alignment_score += 0.4
            
            # Check for premium materials
            formulation = fm_data.get('formula', fm_data.get('formulation', {}))
            if any('K72' in mat for mat in formulation.keys()):
                alignment_score += 0.2
        
        # Eco-friendly intent
        elif primary_intent == 'eco_friendly':
            formulation = fm_data.get('formula', fm_data.get('formulation', {}))
            eco_materials = ['DOTP', 'DINP', 'Ca_Zn']
            if any(mat in formulation for mat in eco_materials):
                alignment_score += 0.3
            
            # Penalty for non-eco materials
            non_eco_materials = ['DOP', 'DBP', 'Ba_Zn']
            if any(mat in formulation for mat in non_eco_materials):
                alignment_score -= 0.1
        
        return max(0.0, min(1.0, alignment_score))
    
    def _generate_recommendation_next_steps(self, fm_data: Dict[str, Any], cost_analysis: Dict[str, Any], 
                                          compliance: Dict[str, Any], risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate specific next steps for each recommendation."""
        next_steps = []
        
        # Compliance-based steps
        compliance_verdict = compliance.get('verdict', 'UNKNOWN')
        if compliance_verdict == 'FAIL':
            failed_props = [d for d in compliance.get('details', []) if d.get('status') == 'FAIL']
            if failed_props:
                next_steps.append(f"Optimize formulation to improve: {', '.join(p['property'] for p in failed_props)}")
        elif compliance_verdict == 'UNKNOWN':
            next_steps.append(f"Conduct testing to verify {compliance.get('standard', 'quality')} compliance")
        
        # Cost-based steps
        supplier_risks = cost_analysis.get('supplier_risks', [])
        if supplier_risks:
            next_steps.append("Verify supplier availability and negotiate pricing")
        
        # Risk-based steps
        risk_level = risk_assessment.get('risk_level', 'MEDIUM')
        if risk_level == 'HIGH':
            next_steps.append("Conduct risk mitigation analysis before production")
        
        identified_risks = risk_assessment.get('identified_risks', [])
        if any('Complex formulation' in risk for risk in identified_risks):
            next_steps.append("Consider formulation simplification for easier processing")
        
        # General steps
        next_steps.append("Prepare 50kg trial batch for validation testing")
        next_steps.append("Conduct full property testing and compliance verification")
        
        if not next_steps:
            next_steps.append("Proceed with production planning and quality assurance setup")
        
        return next_steps[:5]  # Limit to top 5 steps
    
    def _validate_recommendations(self, recommendations: List[GraphRAGRecommendation], 
                                request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate and convert recommendations to final format."""
        validated = []
        
        for rec in recommendations:
            try:
                # Convert to dictionary format
                rec_dict = {
                    'formulation_id': rec.formulation_id,
                    'name': rec.name,
                    'formulation': rec.formulation,
                    'cost_analysis': rec.cost_analysis,
                    'properties': rec.properties,
                    'compliance': rec.compliance,
                    'risk_assessment': rec.risk_assessment,
                    'semantic_score': rec.semantic_score,
                    'graph_score': rec.graph_score,
                    'combined_score': rec.combined_score,
                    'confidence': rec.confidence,
                    'reasoning_path': rec.reasoning_path,
                    'materials_info': rec.materials_info,
                    'suppliers_info': rec.suppliers_info,
                    'next_steps': rec.next_steps,
                    'source': 'GRAPHRAG_ENHANCED'
                }
                
                # Validate against minimum requirements
                if rec.confidence >= Config.MIN_CONFIDENCE_SCORE:
                    validated.append(rec_dict)
                
            except Exception as e:
                logger.warning(f"Failed to validate recommendation {rec.formulation_id}: {e}")
                continue
        
        return validated
    
    def _generate_formulation_insights(self, recommendations: List[Dict[str, Any]], 
                                     query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-level insights about the formulation recommendations."""
        if not recommendations:
            return {'message': 'No suitable formulations found'}
        
        insights = {}
        
        # Cost insights
        costs = [r['cost_analysis'].get('total_cost_per_kg', 0) for r in recommendations if r['cost_analysis'].get('total_cost_per_kg')]
        if costs:
            insights['cost_analysis'] = {
                'min_cost': min(costs),
                'max_cost': max(costs),
                'avg_cost': sum(costs) / len(costs),
                'cost_range': f"₹{min(costs):.1f} - ₹{max(costs):.1f}/kg"
            }
        
        # Compliance insights
        compliance_verdicts = [r['compliance'].get('verdict', 'UNKNOWN') for r in recommendations]
        compliance_counts = {verdict: compliance_verdicts.count(verdict) for verdict in set(compliance_verdicts)}
        insights['compliance_summary'] = compliance_counts
        
        # Risk insights
        risk_levels = [r['risk_assessment'].get('risk_level', 'MEDIUM') for r in recommendations]
        risk_counts = {level: risk_levels.count(level) for level in set(risk_levels)}
        insights['risk_distribution'] = risk_counts
        
        # Material insights
        all_materials = set()
        for rec in recommendations:
            formulation = rec.get('formulation', {})
            all_materials.update(formulation.keys())
        
        insights['common_materials'] = list(all_materials)
        
        # Intent alignment insights
        primary_intent = query_analysis.get('primary_intent', 'general_formulation')
        intent_scores = [self._calculate_intent_alignment_score({'formulation_data': rec}, query_analysis) 
                        for rec in recommendations]
        
        if intent_scores:
            insights['intent_alignment'] = {
                'primary_intent': primary_intent,
                'avg_alignment_score': sum(intent_scores) / len(intent_scores),
                'best_alignment_score': max(intent_scores)
            }
        
        return insights
    
    def _generate_next_steps(self, recommendations: List[Dict[str, Any]], request: Dict[str, Any]) -> List[str]:
        """Generate overall next steps for the formulation project."""
        if not recommendations:
            return ["Expand search criteria or consider alternative approaches"]
        
        next_steps = []
        
        # Based on top recommendation
        top_rec = recommendations[0]
        
        # Compliance-based steps
        if top_rec['compliance'].get('verdict') == 'PASS':
            next_steps.append("Proceed with trial batch production of top recommendation")
        else:
            next_steps.append("Conduct compliance testing and optimization")
        
        # Cost-based steps
        cost_per_kg = top_rec['cost_analysis'].get('total_cost_per_kg', 0)
        cost_limit = request.get('cost_limit', 70.0)
        
        if cost_per_kg > cost_limit:
            next_steps.append("Optimize formulation for cost reduction")
        else:
            next_steps.append("Finalize supplier agreements and pricing")
        
        # Risk-based steps
        risk_level = top_rec['risk_assessment'].get('risk_level', 'MEDIUM')
        if risk_level == 'HIGH':
            next_steps.append("Implement risk mitigation strategies")
        
        # General steps
        next_steps.extend([
            "Set up quality control procedures",
            "Plan production scale-up strategy",
            "Prepare documentation for regulatory compliance"
        ])
        
        return next_steps[:5]  # Limit to top 5 steps
    
    def _calculate_overall_confidence(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence in the recommendations."""
        if not recommendations:
            return 0.0
        
        # Weight by combined scores
        total_weighted_confidence = 0.0
        total_weight = 0.0
        
        for rec in recommendations[:3]:  # Top 3 recommendations
            confidence = rec.get('confidence', 0.5)
            weight = rec.get('combined_score', 0.5)
            
            total_weighted_confidence += confidence * weight
            total_weight += weight
        
        if total_weight > 0:
            return round(total_weighted_confidence / total_weight, 2)
        else:
            return 0.5
    
    def _update_performance_metrics(self, processing_time: float) -> None:
        """Update performance tracking metrics."""
        self.query_count += 1
        self.total_processing_time += processing_time
        
        if self.query_count % 10 == 0:  # Log every 10 queries
            avg_time = self.total_processing_time / self.query_count
            logger.info(f"Performance metrics: {self.query_count} queries, avg time: {avg_time:.2f}s")
    
    # Helper methods
    def _get_fallback_material_cost(self, material_name: str) -> float:
        """Get fallback material cost from database."""
        # Simple cost lookup based on material type
        cost_map = {
            'PVC_K70': 87.5,
            'PVC_K72': 92.0,
            'DOP': 220.0,
            'DBP': 210.0,
            'DOTP': 240.0,
            'CaCO3': 15.0,
            'TiO2': 180.0,
            'Ca_Zn': 350.0,
            'Ba_Zn': 320.0
        }
        
        return cost_map.get(material_name, 100.0)  # Default cost
    
    def _normalize_property_names(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize property names to standard format."""
        normalized = {}
        
        name_mapping = {
            'tens_mpa': 'tensile_strength_mpa',
            'elong_pct': 'elongation_percent',
            'hard_shore': 'hardness_shore',
            'brit_temp_c': 'brittleness_temp_c',
            'visc_cps': 'viscosity_cps'
        }
        
        for key, value in properties.items():
            normalized_key = name_mapping.get(key, key)
            normalized[normalized_key] = value
        
        return normalized
    
    def _generate_risk_mitigation(self, risks: List[str], risk_scores: Dict[str, float]) -> List[str]:
        """Generate risk mitigation suggestions."""
        mitigations = []
        
        # Cost risk mitigation
        if risk_scores.get('cost_risk', 0) > 0.5:
            mitigations.append("Consider alternative lower-cost materials or suppliers")
        
        # Supplier risk mitigation
        if risk_scores.get('supplier_risk', 0) > 0.3:
            mitigations.append("Establish backup suppliers and safety stock")
        
        # Availability risk mitigation
        if risk_scores.get('availability_risk', 0) > 0.3:
            mitigations.append("Negotiate long-term supply agreements")
        
        # Complexity risk mitigation
        if risk_scores.get('complexity_risk', 0) > 0.3:
            mitigations.append("Simplify formulation or improve process controls")
        
        # Quality risk mitigation
        if risk_scores.get('quality_risk', 0) > 0.5:
            mitigations.append("Conduct additional testing and validation")
        
        return mitigations[:3]  # Top 3 mitigations
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        return {
            'agent_type': 'GraphRAG_Enhanced',
            'status': 'ACTIVE',
            'query_count': self.query_count,
            'avg_processing_time': round(self.total_processing_time / max(1, self.query_count), 2),
            'graph_statistics': self.graphrag_engine.get_graph_statistics(),
            'capabilities': [
                'Semantic query understanding',
                'Graph-based formulation search',
                'Multi-factor recommendation scoring',
                'Comprehensive risk assessment',
                'Supplier integration',
                'Real-time cost analysis'
            ]
        }


# Global GraphRAG agent instance
graphrag_agent = GraphRAGFormulationAgent()