"""Production GraphRAG Knowledge Graph Engine for Chemical Formulation Intelligence."""

import numpy as np
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from collections import defaultdict, Counter
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import pickle
import threading
import time
from pathlib import Path

from config import Config
from exceptions import KnowledgeGraphError, SemanticSearchError, ExceptionHandler
from logging_config import get_logger, RequestLogger, PerformanceLogger
from data_layer import db_manager

logger = get_logger(__name__)
perf_logger = PerformanceLogger(__name__)


@dataclass
class GraphEntity:
    """Knowledge graph entity with semantic properties."""
    
    id: str
    type: str  # 'material', 'formulation', 'supplier', 'application', 'property'
    name: str
    properties: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    connections: Optional[Set[str]] = None
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = set()


@dataclass
class GraphRelation:
    """Knowledge graph relation with semantic weight."""
    
    source_id: str
    target_id: str
    relation_type: str  # 'contains', 'supplies', 'compatible', 'alternative', 'improves'
    weight: float
    properties: Dict[str, Any]
    confidence: float = 1.0


class SemanticVectorizer:
    """Advanced semantic vectorization for chemical domain."""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words='english',
            lowercase=True,
            token_pattern=r'[A-Za-z_][A-Za-z0-9_]*'
        )
        self.svd_reducer = TruncatedSVD(n_components=100, random_state=42)
        self.is_fitted = False
        
        # Chemical domain vocabulary
        self.chemical_terms = {
            'pvc', 'plasticizer', 'stabilizer', 'filler', 'additive',
            'tensile', 'elongation', 'hardness', 'viscosity', 'brittleness',
            'dop', 'dbp', 'dotp', 'dinp', 'caco3', 'tio2', 'ca_zn', 'ba_zn',
            'cable', 'insulation', 'pipe', 'film', 'sheet', 'profile',
            'compliance', 'standard', 'rohs', 'reach', 'is_5831'
        }
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """Fit vectorizer and transform texts to semantic vectors."""
        try:
            # Enhance texts with chemical domain knowledge
            enhanced_texts = [self._enhance_text(text) for text in texts]
            
            # TF-IDF transformation
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(enhanced_texts)
            
            # Dimensionality reduction
            reduced_vectors = self.svd_reducer.fit_transform(tfidf_matrix)
            
            self.is_fitted = True
            logger.info(f"Semantic vectorizer fitted on {len(texts)} texts")
            
            return reduced_vectors
            
        except Exception as e:
            raise SemanticSearchError(f"Vectorization failed: {e}")
    
    def transform(self, texts: List[str]) -> np.ndarray:
        """Transform new texts using fitted vectorizer."""
        if not self.is_fitted:
            raise SemanticSearchError("Vectorizer not fitted yet")
        
        try:
            enhanced_texts = [self._enhance_text(text) for text in texts]
            tfidf_matrix = self.tfidf_vectorizer.transform(enhanced_texts)
            reduced_vectors = self.svd_reducer.transform(tfidf_matrix)
            
            return reduced_vectors
            
        except Exception as e:
            raise SemanticSearchError(f"Text transformation failed: {e}")
    
    def _enhance_text(self, text: str) -> str:
        """Enhance text with chemical domain knowledge."""
        enhanced = text.lower()
        
        # Add chemical synonyms and expansions
        replacements = {
            'pvc': 'pvc polyvinyl chloride polymer',
            'dop': 'dop dioctyl phthalate plasticizer',
            'caco3': 'caco3 calcium carbonate filler',
            'tensile': 'tensile strength mechanical property',
            'elongation': 'elongation flexibility stretch',
            'cable': 'cable wire insulation electrical',
            'pipe': 'pipe plumbing water pressure'
        }
        
        for term, expansion in replacements.items():
            if term in enhanced:
                enhanced = enhanced.replace(term, expansion)
        
        return enhanced


class GraphRAGEngine:
    """Production GraphRAG engine with advanced semantic reasoning."""
    
    def __init__(self):
        """Initialize GraphRAG engine with all components."""
        try:
            # Initialize core components
            self.graph = nx.MultiDiGraph()
            self.entities: Dict[str, GraphEntity] = {}
            self.relations: List[GraphRelation] = []
            self.vectorizer = SemanticVectorizer()
            
            # Performance tracking
            self.query_cache: Dict[str, Any] = {}
            self.cache_lock = threading.Lock()
            
            # Build knowledge graph
            self._build_knowledge_graph()
            
            logger.info("GraphRAG Engine initialized successfully")
            
        except Exception as e:
            raise KnowledgeGraphError(f"Failed to initialize GraphRAG engine: {e}")
    
    @ExceptionHandler.handle_exceptions
    def _build_knowledge_graph(self) -> None:
        """Build comprehensive knowledge graph from all data sources."""
        with perf_logger.timer("knowledge_graph_build"):
            logger.info("Building comprehensive knowledge graph...")
            
            # Extract entities from all databases
            self._extract_material_entities()
            self._extract_formulation_entities()
            self._extract_supplier_entities()
            self._extract_application_entities()
            self._extract_property_entities()
            self._extract_standard_entities()
            
            # Build semantic relationships
            self._build_material_compatibility_relations()
            self._build_supplier_material_relations()
            self._build_formulation_application_relations()
            self._build_property_enhancement_relations()
            self._build_compliance_relations()
            self._build_alternative_material_relations()
            
            # Create semantic embeddings
            self._create_semantic_embeddings()
            
            # Populate NetworkX graph for path analysis
            self._populate_networkx_graph()
            
            logger.info(f"Knowledge graph built: {len(self.entities)} entities, {len(self.relations)} relations")
    
    def _extract_material_entities(self) -> None:
        """Extract material entities with comprehensive properties."""
        ingredients = db_manager.ingredients
        
        if isinstance(ingredients, dict):
            for category, items in ingredients.items():
                if isinstance(items, list):
                    for item in items:
                        material_id = item.get('id', '')
                        if material_id:
                            entity = GraphEntity(
                                id=f"material_{material_id}",
                                type="material",
                                name=item.get('name', material_id),
                                properties={
                                    'category': category.lower(),
                                    'base_cost_per_kg': item.get('cost_per_kg', 0),
                                    'supplier_count': len(item.get('suppliers', [])),
                                    'chemical_properties': item.get('properties', {}),
                                    'compliance_data': item.get('compliance', {}),
                                    'typical_phr_range': item.get('typical_phr', [0, 100]),
                                    'compatibility_score': item.get('compatibility', 1.0)
                                }
                            )
                            self.entities[entity.id] = entity
        
        # Extract from formulations for completeness
        for fm in db_manager.formulations:
            formula = fm.get('formula', fm.get('formulation', {}))
            if isinstance(formula, dict):
                for material, phr_data in formula.items():
                    entity_id = f"material_{material}"
                    if entity_id not in self.entities:
                        phr = phr_data if isinstance(phr_data, (int, float)) else phr_data.get('phr', 0)
                        
                        entity = GraphEntity(
                            id=entity_id,
                            type="material",
                            name=material,
                            properties={
                                'category': 'formulation_ingredient',
                                'usage_frequency': 1,
                                'typical_phr': phr,
                                'source': 'formulation_database'
                            }
                        )
                        self.entities[entity_id] = entity
    
    def _extract_formulation_entities(self) -> None:
        """Extract formulation entities with performance data."""
        for fm in db_manager.formulations:
            fm_id = fm.get('id', '')
            if fm_id:
                entity = GraphEntity(
                    id=f"formulation_{fm_id}",
                    type="formulation",
                    name=f"Formulation {fm_id}",
                    properties={
                        'application': fm.get('app', fm.get('application', '')),
                        'cost_per_kg': fm.get('cost_per_kg', 0),
                        'compliance_verdict': fm.get('verdict', fm.get('compliance_verdict', 'UNKNOWN')),
                        'properties': fm.get('prop', fm.get('properties', {})),
                        'standard': fm.get('std', fm.get('standard', '')),
                        'formulation_data': fm.get('formula', fm.get('formulation', {})),
                        'success_rate': 1.0 if fm.get('verdict') == 'PASS' else 0.5,
                        'complexity_score': len(fm.get('formula', fm.get('formulation', {})))
                    }
                )
                self.entities[entity.id] = entity
    
    def _extract_supplier_entities(self) -> None:
        """Extract supplier entities with reliability metrics."""
        for supplier in db_manager.suppliers:
            supplier_id = supplier.get('id', '')
            if supplier_id:
                entity = GraphEntity(
                    id=f"supplier_{supplier_id}",
                    type="supplier",
                    name=supplier.get('name', ''),
                    properties={
                        'location': supplier.get('loc', supplier.get('location', '')),
                        'reliability_score': supplier.get('rel_score', supplier.get('reliability_score', 0)),
                        'lead_time_days': supplier.get('lead_d', supplier.get('lead_time_days', 0)),
                        'certifications': supplier.get('cert', supplier.get('certifications', '')),
                        'availability': supplier.get('avail', supplier.get('availability', 'Unknown')),
                        'product': supplier.get('prod', supplier.get('product', '')),
                        'price_per_kg': self._normalize_price(supplier.get('price', 0)),
                        'min_order_kg': supplier.get('min_ord', supplier.get('min_order_kg', 0)),
                        'quality_rating': supplier.get('quality', 4.0)
                    }
                )
                self.entities[entity.id] = entity
    
    def _extract_application_entities(self) -> None:
        """Extract application entities with requirements."""
        applications = set()
        app_requirements = defaultdict(list)
        
        # Collect applications and their requirements
        for fm in db_manager.formulations:
            app = fm.get('app', fm.get('application', ''))
            if app:
                applications.add(app)
                properties = fm.get('prop', fm.get('properties', {}))
                if properties:
                    app_requirements[app].append(properties)
        
        for app in applications:
            # Calculate typical property ranges for this application
            typical_properties = {}
            if app_requirements[app]:
                for prop_name in ['tens_mpa', 'elong_pct', 'hard_shore', 'visc_cps']:
                    values = [props.get(prop_name, 0) for props in app_requirements[app] if props.get(prop_name)]
                    if values:
                        typical_properties[prop_name] = {
                            'min': min(values),
                            'max': max(values),
                            'avg': sum(values) / len(values)
                        }
            
            entity = GraphEntity(
                id=f"application_{app}",
                type="application",
                name=app.replace('_', ' ').title(),
                properties={
                    'domain': 'polymer_processing',
                    'typical_properties': typical_properties,
                    'formulation_count': len(app_requirements[app]),
                    'complexity_level': 'high' if len(typical_properties) > 3 else 'medium'
                }
            )
            self.entities[entity.id] = entity
    
    def _extract_property_entities(self) -> None:
        """Extract property entities with measurement details."""
        properties = [
            ('tensile_strength', 'Tensile Strength', 'MPa', 'mechanical', [10, 30]),
            ('elongation', 'Elongation at Break', '%', 'mechanical', [100, 400]),
            ('hardness', 'Shore A Hardness', 'Shore A', 'mechanical', [40, 95]),
            ('brittleness_temp', 'Brittleness Temperature', '°C', 'thermal', [-40, -10]),
            ('viscosity', 'Melt Viscosity', 'cPs', 'rheological', [500, 1500])
        ]
        
        for prop_id, prop_name, unit, category, typical_range in properties:
            entity = GraphEntity(
                id=f"property_{prop_id}",
                type="property",
                name=prop_name,
                properties={
                    'unit': unit,
                    'category': category,
                    'typical_range': typical_range,
                    'measurement_method': f"ASTM_{prop_id.upper()}",
                    'importance_weight': 1.0
                }
            )
            self.entities[entity.id] = entity
    
    def _extract_standard_entities(self) -> None:
        """Extract compliance standard entities with requirements."""
        standards = db_manager.standards
        
        if isinstance(standards, dict):
            for std_id, std_spec in standards.items():
                entity = GraphEntity(
                    id=f"standard_{std_id}",
                    type="standard",
                    name=std_id,
                    properties={
                        'requirements': std_spec,
                        'domain': 'compliance',
                        'region': 'India' if 'IS' in std_id else 'International',
                        'strictness_level': len(std_spec) if isinstance(std_spec, dict) else 1,
                        'industry_adoption': 'high' if 'IS_5831' in std_id else 'medium'
                    }
                )
                self.entities[entity.id] = entity
    
    def _build_material_compatibility_relations(self) -> None:
        """Build material compatibility relationships from formulation co-occurrence."""
        material_cooccurrence = defaultdict(lambda: defaultdict(int))
        material_performance = defaultdict(list)
        
        # Analyze formulations for material interactions
        for fm in db_manager.formulations:
            formula = fm.get('formula', fm.get('formulation', {}))
            verdict = fm.get('verdict', fm.get('compliance_verdict', 'UNKNOWN'))
            
            if isinstance(formula, dict):
                materials = list(formula.keys())
                performance_score = 1.0 if verdict == 'PASS' else 0.5
                
                # Track co-occurrence and performance
                for i, mat1 in enumerate(materials):
                    material_performance[mat1].append(performance_score)
                    for mat2 in materials[i+1:]:
                        material_cooccurrence[mat1][mat2] += 1
                        material_cooccurrence[mat2][mat1] += 1
        
        # Create compatibility relations
        for mat1, mat2_counts in material_cooccurrence.items():
            for mat2, count in mat2_counts.items():
                if count >= 2:  # Appeared together at least twice
                    # Calculate compatibility score
                    mat1_avg_perf = sum(material_performance[mat1]) / len(material_performance[mat1])
                    mat2_avg_perf = sum(material_performance[mat2]) / len(material_performance[mat2])
                    
                    compatibility_score = min(1.0, (count / 10.0) * (mat1_avg_perf + mat2_avg_perf) / 2)
                    
                    relation = GraphRelation(
                        source_id=f"material_{mat1}",
                        target_id=f"material_{mat2}",
                        relation_type="COMPATIBLE_WITH",
                        weight=compatibility_score,
                        properties={
                            'cooccurrence_count': count,
                            'avg_performance': (mat1_avg_perf + mat2_avg_perf) / 2,
                            'confidence': min(1.0, count / 5.0)
                        },
                        confidence=min(1.0, count / 5.0)
                    )
                    self.relations.append(relation)
    
    def _build_supplier_material_relations(self) -> None:
        """Build supplier-material supply relationships."""
        for supplier in db_manager.suppliers:
            supplier_id = supplier.get('id', '')
            product = supplier.get('prod', supplier.get('product', ''))
            
            if supplier_id and product:
                # Normalize price
                price = self._normalize_price(supplier.get('price', 0))
                reliability = supplier.get('rel_score', supplier.get('reliability_score', 0)) / 5.0
                
                # Calculate supply quality score
                availability = supplier.get('avail', supplier.get('availability', 'Unknown'))
                availability_score = 1.0 if availability == 'Yes' else 0.5 if availability == 'Limited' else 0.2
                
                supply_quality = (reliability + availability_score) / 2
                
                relation = GraphRelation(
                    source_id=f"supplier_{supplier_id}",
                    target_id=f"material_{product}",
                    relation_type="SUPPLIES",
                    weight=supply_quality,
                    properties={
                        'price_per_kg': price,
                        'availability': availability,
                        'lead_time_days': supplier.get('lead_d', supplier.get('lead_time_days', 0)),
                        'min_order_kg': supplier.get('min_ord', supplier.get('min_order_kg', 0)),
                        'reliability_score': reliability,
                        'certifications': supplier.get('cert', supplier.get('certifications', ''))
                    },
                    confidence=reliability
                )
                self.relations.append(relation)
    
    def _build_formulation_application_relations(self) -> None:
        """Build formulation-application suitability relationships."""
        for fm in db_manager.formulations:
            fm_id = fm.get('id', '')
            app = fm.get('app', fm.get('application', ''))
            
            if fm_id and app:
                verdict = fm.get('verdict', fm.get('compliance_verdict', 'UNKNOWN'))
                cost = fm.get('cost_per_kg', 0)
                
                # Calculate suitability score
                compliance_score = 1.0 if verdict == 'PASS' else 0.7 if verdict == 'BORDERLINE' else 0.3
                cost_score = max(0.1, min(1.0, (100 - cost) / 50))  # Lower cost = higher score
                
                suitability = (compliance_score + cost_score) / 2
                
                relation = GraphRelation(
                    source_id=f"formulation_{fm_id}",
                    target_id=f"application_{app}",
                    relation_type="SUITABLE_FOR",
                    weight=suitability,
                    properties={
                        'cost_per_kg': cost,
                        'compliance_verdict': verdict,
                        'standard': fm.get('std', fm.get('standard', '')),
                        'properties': fm.get('prop', fm.get('properties', {}))
                    },
                    confidence=compliance_score
                )
                self.relations.append(relation)
                
                # Build formulation-material containment relations
                formula = fm.get('formula', fm.get('formulation', {}))
                if isinstance(formula, dict):
                    for material, phr_data in formula.items():
                        phr = phr_data if isinstance(phr_data, (int, float)) else phr_data.get('phr', 0)
                        
                        # Weight by PHR proportion
                        total_phr = sum(
                            p if isinstance(p, (int, float)) else p.get('phr', 0) 
                            for p in formula.values()
                        )
                        proportion = phr / total_phr if total_phr > 0 else 0
                        
                        relation = GraphRelation(
                            source_id=f"formulation_{fm_id}",
                            target_id=f"material_{material}",
                            relation_type="CONTAINS",
                            weight=min(1.0, proportion * 2),  # Scale proportion
                            properties={
                                'phr': phr,
                                'proportion': proportion,
                                'role': self._determine_material_role(material)
                            },
                            confidence=1.0
                        )
                        self.relations.append(relation)
    
    def _build_property_enhancement_relations(self) -> None:
        """Build material-property enhancement relationships."""
        # Define material-property enhancement rules based on chemical knowledge
        enhancement_rules = {
            'PVC_K72': [('tensile_strength', 0.8), ('hardness', 0.6)],
            'PVC_K70': [('tensile_strength', 0.6), ('hardness', 0.4)],
            'DOP': [('elongation', 0.9), ('brittleness_temp', 0.7)],
            'DBP': [('elongation', 0.8), ('brittleness_temp', 0.6)],
            'DOTP': [('elongation', 0.7), ('brittleness_temp', 0.8)],
            'CaCO3': [('hardness', 0.8), ('tensile_strength', -0.3)],  # Negative = reduces
            'TiO2': [('hardness', 0.6), ('tensile_strength', 0.2)],
            'Ca_Zn': [('brittleness_temp', 0.4)],
            'Ba_Zn': [('brittleness_temp', 0.5)]
        }
        
        for material, property_effects in enhancement_rules.items():
            for property_name, effect_strength in property_effects:
                relation_type = "ENHANCES" if effect_strength > 0 else "REDUCES"
                
                relation = GraphRelation(
                    source_id=f"material_{material}",
                    target_id=f"property_{property_name}",
                    relation_type=relation_type,
                    weight=abs(effect_strength),
                    properties={
                        'effect_strength': effect_strength,
                        'mechanism': self._get_enhancement_mechanism(material, property_name),
                        'typical_phr_range': self._get_typical_phr_range(material)
                    },
                    confidence=0.8  # Based on chemical knowledge
                )
                self.relations.append(relation)
    
    def _build_compliance_relations(self) -> None:
        """Build formulation-standard compliance relationships."""
        for fm in db_manager.formulations:
            fm_id = fm.get('id', '')
            standard = fm.get('std', fm.get('standard', ''))
            verdict = fm.get('verdict', fm.get('compliance_verdict', ''))
            
            if fm_id and standard:
                compliance_weight = {
                    'PASS': 1.0,
                    'BORDERLINE': 0.7,
                    'FAIL': 0.2,
                    'UNKNOWN': 0.5
                }.get(verdict, 0.5)
                
                relation = GraphRelation(
                    source_id=f"formulation_{fm_id}",
                    target_id=f"standard_{standard}",
                    relation_type="COMPLIES_WITH" if verdict == 'PASS' else "TESTED_AGAINST",
                    weight=compliance_weight,
                    properties={
                        'verdict': verdict,
                        'test_results': fm.get('prop', fm.get('properties', {})),
                        'margin_of_safety': self._calculate_safety_margin(fm, standard)
                    },
                    confidence=1.0 if verdict in ['PASS', 'FAIL'] else 0.5
                )
                self.relations.append(relation)
    
    def _build_alternative_material_relations(self) -> None:
        """Build alternative material relationships based on similar usage patterns."""
        material_usage_patterns = defaultdict(list)
        
        # Analyze usage patterns
        for fm in db_manager.formulations:
            formula = fm.get('formula', fm.get('formulation', {}))
            app = fm.get('app', fm.get('application', ''))
            
            if isinstance(formula, dict) and app:
                for material, phr_data in formula.items():
                    phr = phr_data if isinstance(phr_data, (int, float)) else phr_data.get('phr', 0)
                    material_usage_patterns[material].append({
                        'application': app,
                        'phr': phr,
                        'formulation_id': fm.get('id', '')
                    })
        
        # Find materials with similar usage patterns
        materials = list(material_usage_patterns.keys())
        for i, mat1 in enumerate(materials):
            for mat2 in materials[i+1:]:
                similarity = self._calculate_usage_similarity(
                    material_usage_patterns[mat1],
                    material_usage_patterns[mat2]
                )
                
                if similarity > 0.3:  # Threshold for alternative relationship
                    relation = GraphRelation(
                        source_id=f"material_{mat1}",
                        target_id=f"material_{mat2}",
                        relation_type="ALTERNATIVE_TO",
                        weight=similarity,
                        properties={
                            'similarity_score': similarity,
                            'substitution_ratio': self._calculate_substitution_ratio(mat1, mat2),
                            'performance_impact': 'minimal' if similarity > 0.7 else 'moderate'
                        },
                        confidence=similarity
                    )
                    self.relations.append(relation)
    
    def _create_semantic_embeddings(self) -> None:
        """Create semantic embeddings for all entities."""
        try:
            # Prepare texts for all entities
            entity_texts = []
            entity_ids = []
            
            for entity_id, entity in self.entities.items():
                # Create comprehensive text representation
                text_parts = [entity.name, entity.type]
                
                # Add property values as text
                for key, value in entity.properties.items():
                    if isinstance(value, str):
                        text_parts.append(value)
                    elif isinstance(value, dict):
                        text_parts.extend([str(v) for v in value.values() if isinstance(v, str)])
                    elif isinstance(value, (int, float)):
                        text_parts.append(f"{key}_{value}")
                
                entity_text = ' '.join(text_parts).lower()
                entity_texts.append(entity_text)
                entity_ids.append(entity_id)
            
            # Create embeddings
            if entity_texts:
                embeddings = self.vectorizer.fit_transform(entity_texts)
                
                for i, entity_id in enumerate(entity_ids):
                    self.entities[entity_id].embedding = embeddings[i]
                
                logger.info(f"Created semantic embeddings for {len(entity_ids)} entities")
            
        except Exception as e:
            logger.error(f"Failed to create semantic embeddings: {e}")
            raise SemanticSearchError(f"Embedding creation failed: {e}")
    
    def _populate_networkx_graph(self) -> None:
        """Populate NetworkX graph for advanced path analysis."""
        try:
            # Add nodes with attributes
            for entity_id, entity in self.entities.items():
                # Filter out conflicting keys from properties
                node_props = {k: v for k, v in entity.properties.items() 
                             if k not in ['type', 'name']}
                
                self.graph.add_node(
                    entity_id,
                    type=entity.type,
                    name=entity.name,
                    **node_props
                )
            
            # Add edges with attributes
            for relation in self.relations:
                # Filter out conflicting keys from properties
                edge_props = {k: v for k, v in relation.properties.items() 
                             if k not in ['relation_type', 'weight', 'confidence']}
                
                self.graph.add_edge(
                    relation.source_id,
                    relation.target_id,
                    relation_type=relation.relation_type,
                    weight=relation.weight,
                    confidence=relation.confidence,
                    **edge_props
                )
            
            logger.info(f"NetworkX graph populated: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
            
        except Exception as e:
            logger.error(f"Failed to populate NetworkX graph: {e}")
    
    def semantic_search(self, query: str, entity_types: List[str] = None, top_k: int = 10) -> List[Tuple[str, float]]:
        """Advanced semantic search with entity type filtering."""
        try:
            with perf_logger.timer("semantic_search"):
                # Check cache first
                cache_key = f"{query}_{entity_types}_{top_k}"
                with self.cache_lock:
                    if cache_key in self.query_cache:
                        return self.query_cache[cache_key]
                
                # Transform query to embedding
                query_embedding = self.vectorizer.transform([query])[0]
                
                # Calculate similarities
                similarities = []
                for entity_id, entity in self.entities.items():
                    # Filter by entity type if specified
                    if entity_types and entity.type not in entity_types:
                        continue
                    
                    if entity.embedding is not None:
                        similarity = cosine_similarity(
                            query_embedding.reshape(1, -1),
                            entity.embedding.reshape(1, -1)
                        )[0][0]
                        
                        if similarity > 0.1:  # Minimum similarity threshold
                            similarities.append((entity_id, similarity))
                
                # Sort and get top results
                similarities.sort(key=lambda x: x[1], reverse=True)
                results = similarities[:top_k]
                
                # Cache results
                with self.cache_lock:
                    self.query_cache[cache_key] = results
                
                return results
                
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            raise SemanticSearchError(f"Search failed: {e}")
    
    def find_formulation_paths(self, query: str, constraints: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find formulation recommendations using graph path analysis."""
        try:
            with perf_logger.timer("formulation_path_search"):
                results = []
                
                # 1. Semantic search for relevant entities
                semantic_results = self.semantic_search(query, top_k=20)
                
                # 2. Find applications from semantic results
                applications = []
                for entity_id, score in semantic_results:
                    if entity_id.startswith('application_'):
                        app_name = entity_id.replace('application_', '')
                        applications.append((app_name, score))
                
                # 3. Find formulations for each application
                for app_name, semantic_score in applications:
                    app_formulations = self._find_formulations_for_application(app_name, constraints)
                    
                    for result in app_formulations:
                        result['semantic_score'] = semantic_score
                        result['combined_score'] = (semantic_score + result['graph_weight']) / 2
                        results.append(result)
                
                # 4. Direct formulation search
                for entity_id, score in semantic_results:
                    if entity_id.startswith('formulation_'):
                        fm_result = self._get_formulation_details(entity_id, score, constraints)
                        if fm_result:
                            results.append(fm_result)
                
                # 5. Remove duplicates and rank
                unique_results = self._deduplicate_and_rank(results)
                
                return unique_results[:10]  # Top 10 results
                
        except Exception as e:
            logger.error(f"Formulation path search failed: {e}")
            raise KnowledgeGraphError(f"Path search failed: {e}")
    
    def _find_formulations_for_application(self, application: str, constraints: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find formulations suitable for specific application."""
        app_entity_id = f"application_{application}"
        formulation_results = []
        
        if app_entity_id in self.graph:
            # Find formulations connected to this application
            for neighbor in self.graph.neighbors(app_entity_id):
                if neighbor.startswith('formulation_'):
                    edge_data = self.graph.get_edge_data(neighbor, app_entity_id)
                    if edge_data:
                        # Get the best edge (highest weight)
                        best_edge = max(edge_data.values(), key=lambda x: x.get('weight', 0))
                        
                        fm_result = self._get_formulation_details(
                            neighbor, 
                            best_edge.get('weight', 0.5), 
                            constraints
                        )
                        if fm_result:
                            formulation_results.append(fm_result)
        
        return formulation_results
    
    def _get_formulation_details(self, formulation_entity_id: str, base_score: float, constraints: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Get detailed formulation information."""
        fm_id = formulation_entity_id.replace('formulation_', '')
        
        # Find formulation in database
        for fm in db_manager.formulations:
            if fm.get('id') == fm_id:
                # Apply constraints
                if constraints:
                    cost_limit = constraints.get('cost_limit')
                    if cost_limit and fm.get('cost_per_kg', 0) > cost_limit:
                        return None
                
                # Get materials and suppliers
                materials = self._get_formulation_materials(formulation_entity_id)
                suppliers = self._get_material_suppliers(materials)
                
                return {
                    'formulation_id': fm_id,
                    'formulation_data': fm,
                    'materials': materials,
                    'suppliers': suppliers,
                    'graph_weight': base_score,
                    'semantic_score': base_score,
                    'combined_score': base_score
                }
        
        return None
    
    def _get_formulation_materials(self, formulation_entity_id: str) -> List[Dict[str, Any]]:
        """Get materials contained in formulation with details."""
        materials = []
        
        if formulation_entity_id in self.graph:
            for neighbor in self.graph.neighbors(formulation_entity_id):
                if neighbor.startswith('material_'):
                    edge_data = self.graph.get_edge_data(formulation_entity_id, neighbor)
                    if edge_data:
                        # Get containment relation
                        contains_edges = [e for e in edge_data.values() 
                                        if e.get('relation_type') == 'CONTAINS']
                        
                        if contains_edges:
                            best_edge = max(contains_edges, key=lambda x: x.get('weight', 0))
                            material_name = neighbor.replace('material_', '')
                            
                            material_info = {
                                'name': material_name,
                                'phr': best_edge.get('phr', 0),
                                'proportion': best_edge.get('proportion', 0),
                                'role': best_edge.get('role', 'unknown'),
                                'entity_id': neighbor
                            }
                            
                            # Add entity properties if available
                            if neighbor in self.entities:
                                material_info['properties'] = self.entities[neighbor].properties
                            
                            materials.append(material_info)
        
        return materials
    
    def _get_material_suppliers(self, materials: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Get suppliers for materials with detailed information."""
        suppliers = {}
        
        for material in materials:
            material_entity_id = material.get('entity_id', f"material_{material['name']}")
            material_suppliers = []
            
            if material_entity_id in self.graph:
                # Find suppliers connected to this material
                for neighbor in self.graph.predecessors(material_entity_id):
                    if neighbor.startswith('supplier_'):
                        edge_data = self.graph.get_edge_data(neighbor, material_entity_id)
                        if edge_data:
                            # Get supply relation
                            supply_edges = [e for e in edge_data.values() 
                                          if e.get('relation_type') == 'SUPPLIES']
                            
                            if supply_edges:
                                best_edge = max(supply_edges, key=lambda x: x.get('weight', 0))
                                
                                supplier_info = {
                                    'entity_id': neighbor,
                                    'reliability': best_edge.get('weight', 0.5),
                                    'price_per_kg': best_edge.get('price_per_kg', 0),
                                    'availability': best_edge.get('availability', 'Unknown'),
                                    'lead_time_days': best_edge.get('lead_time_days', 0),
                                    'min_order_kg': best_edge.get('min_order_kg', 0)
                                }
                                
                                # Add entity properties
                                if neighbor in self.entities:
                                    supplier_info.update(self.entities[neighbor].properties)
                                
                                material_suppliers.append(supplier_info)
            
            # Sort suppliers by reliability and price
            material_suppliers.sort(key=lambda x: (-x['reliability'], x['price_per_kg']))
            suppliers[material['name']] = material_suppliers
        
        return suppliers
    
    def _deduplicate_and_rank(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and rank results by combined score."""
        seen_formulations = set()
        unique_results = []
        
        for result in results:
            fm_id = result['formulation_id']
            if fm_id not in seen_formulations:
                seen_formulations.add(fm_id)
                unique_results.append(result)
        
        # Sort by combined score
        unique_results.sort(key=lambda x: x['combined_score'], reverse=True)
        return unique_results
    
    # Helper methods
    def _normalize_price(self, price: Union[int, float]) -> float:
        """Normalize price to ₹/kg."""
        if isinstance(price, (int, float)) and price > 1000:
            return price / 1000  # Convert ₹/ton to ₹/kg
        return float(price)
    
    def _determine_material_role(self, material: str) -> str:
        """Determine the role of material in formulation."""
        material_lower = material.lower()
        
        if 'pvc' in material_lower:
            return 'base_polymer'
        elif any(p in material_lower for p in ['dop', 'dbp', 'dotp', 'dinp']):
            return 'plasticizer'
        elif any(f in material_lower for f in ['caco3', 'tio2', 'talc']):
            return 'filler'
        elif any(s in material_lower for s in ['ca_zn', 'ba_zn', 'pb']):
            return 'stabilizer'
        else:
            return 'additive'
    
    def _get_enhancement_mechanism(self, material: str, property_name: str) -> str:
        """Get the mechanism by which material affects property."""
        mechanisms = {
            ('PVC_K72', 'tensile_strength'): 'Higher molecular weight increases chain entanglement',
            ('DOP', 'elongation'): 'Plasticizer increases chain mobility',
            ('CaCO3', 'hardness'): 'Rigid filler particles increase stiffness',
            ('Ca_Zn', 'brittleness_temp'): 'Stabilizer prevents degradation at low temperatures'
        }
        return mechanisms.get((material, property_name), 'Chemical interaction mechanism')
    
    def _get_typical_phr_range(self, material: str) -> List[float]:
        """Get typical PHR range for material."""
        ranges = {
            'PVC_K70': [100, 100],  # Base polymer
            'PVC_K72': [100, 100],
            'DOP': [30, 50],
            'DBP': [25, 45],
            'DOTP': [35, 55],
            'CaCO3': [5, 15],
            'TiO2': [2, 8],
            'Ca_Zn': [1, 3],
            'Ba_Zn': [1, 3]
        }
        return ranges.get(material, [0, 10])
    
    def _calculate_safety_margin(self, formulation: Dict[str, Any], standard: str) -> float:
        """Calculate safety margin for compliance."""
        properties = formulation.get('prop', formulation.get('properties', {}))
        standards = db_manager.standards
        
        if standard in standards and isinstance(standards[standard], dict):
            std_reqs = standards[standard]
            margins = []
            
            for prop, value in properties.items():
                if prop in std_reqs and isinstance(value, (int, float)):
                    req = std_reqs[prop]
                    if isinstance(req, dict):
                        min_val = req.get('min', float('-inf'))
                        max_val = req.get('max', float('inf'))
                        
                        if min_val != float('-inf'):
                            margin = (value - min_val) / min_val if min_val > 0 else 0
                            margins.append(margin)
                        
                        if max_val != float('inf'):
                            margin = (max_val - value) / max_val if max_val > 0 else 0
                            margins.append(margin)
            
            return sum(margins) / len(margins) if margins else 0.0
        
        return 0.0
    
    def _calculate_usage_similarity(self, usage1: List[Dict], usage2: List[Dict]) -> float:
        """Calculate similarity between material usage patterns."""
        if not usage1 or not usage2:
            return 0.0
        
        # Compare applications
        apps1 = set(u['application'] for u in usage1)
        apps2 = set(u['application'] for u in usage2)
        app_similarity = len(apps1 & apps2) / len(apps1 | apps2) if apps1 | apps2 else 0
        
        # Compare PHR ranges
        phr1 = [u['phr'] for u in usage1 if u['phr'] > 0]
        phr2 = [u['phr'] for u in usage2 if u['phr'] > 0]
        
        if phr1 and phr2:
            avg_phr1 = sum(phr1) / len(phr1)
            avg_phr2 = sum(phr2) / len(phr2)
            phr_similarity = 1 - abs(avg_phr1 - avg_phr2) / max(avg_phr1, avg_phr2)
        else:
            phr_similarity = 0
        
        return (app_similarity + phr_similarity) / 2
    
    def _calculate_substitution_ratio(self, mat1: str, mat2: str) -> float:
        """Calculate substitution ratio between materials."""
        # Simplified substitution ratio based on material types
        role1 = self._determine_material_role(mat1)
        role2 = self._determine_material_role(mat2)
        
        if role1 == role2:
            # Same role materials can often substitute 1:1
            return 1.0
        else:
            # Different roles may require adjustment
            return 0.8
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics."""
        return {
            'entities': {
                'total': len(self.entities),
                'by_type': Counter(e.type for e in self.entities.values())
            },
            'relations': {
                'total': len(self.relations),
                'by_type': Counter(r.relation_type for r in self.relations)
            },
            'graph_metrics': {
                'nodes': self.graph.number_of_nodes(),
                'edges': self.graph.number_of_edges(),
                'density': nx.density(self.graph),
                'connected_components': nx.number_weakly_connected_components(self.graph)
            },
            'cache_stats': {
                'cached_queries': len(self.query_cache)
            }
        }


# Global GraphRAG engine instance
graphrag_engine = GraphRAGEngine()