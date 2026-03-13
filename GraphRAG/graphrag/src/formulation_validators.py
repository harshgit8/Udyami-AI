"""Production validators for GraphRAG Agent with comprehensive validation."""

import json
import jsonschema
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import re

from exceptions import ValidationError, DatabaseError
from config import Config
from logging_config import get_logger

logger = get_logger(__name__)


# JSON Schema definitions for data validation
FORMULATION_SCHEMA = {
    "type": "object",
    "required": ["id", "app", "formula", "cost_per_kg"],
    "properties": {
        "id": {"type": "string", "pattern": "^FM-\\d{4}$"},
        "app": {"type": "string", "minLength": 1},
        "formula": {
            "type": "object",
            "patternProperties": {
                "^[A-Za-z0-9_]+$": {
                    "oneOf": [
                        {"type": "number", "minimum": 0},
                        {
                            "type": "object",
                            "required": ["phr"],
                            "properties": {
                                "phr": {"type": "number", "minimum": 0}
                            }
                        }
                    ]
                }
            },
            "minProperties": 1
        },
        "cost_per_kg": {"type": "number", "minimum": 0, "maximum": 500},
        "prop": {
            "type": "object",
            "properties": {
                "tens_mpa": {"type": "number", "minimum": 5, "maximum": 50},
                "elong_pct": {"type": "number", "minimum": 50, "maximum": 500},
                "hard_shore": {"type": "number", "minimum": 30, "maximum": 100},
                "brit_temp_c": {"type": "number", "minimum": -50, "maximum": 10},
                "visc_cps": {"type": "number", "minimum": 200, "maximum": 2000}
            }
        },
        "std": {"type": "string"},
        "verdict": {"type": "string", "enum": ["PASS", "FAIL", "BORDERLINE", "UNKNOWN"]}
    }
}

SUPPLIER_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "prod", "price"],
    "properties": {
        "id": {"type": "string", "pattern": "^SUPP-\\d{4}$"},
        "name": {"type": "string", "minLength": 1},
        "prod": {"type": "string", "minLength": 1},
        "price": {"type": "number", "minimum": 0},
        "loc": {"type": "string"},
        "rel_score": {"type": "number", "minimum": 0, "maximum": 5},
        "lead_d": {"type": "integer", "minimum": 0, "maximum": 365},
        "avail": {"type": "string", "enum": ["Yes", "No", "Limited"]},
        "cert": {"type": "string"},
        "min_ord": {"type": "integer", "minimum": 0}
    }
}

INGREDIENT_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^[A-Z_]+$": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "cost_per_kg"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "name": {"type": "string"},
                    "cost_per_kg": {"type": "number", "minimum": 0},
                    "supplier": {"type": "string"},
                    "properties": {"type": "object"},
                    "compliance": {"type": "object"}
                }
            }
        }
    }
}

STANDARDS_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^[A-Z_0-9]+$": {
            "type": "object",
            "patternProperties": {
                "^[a-z_]+$": {
                    "type": "object",
                    "properties": {
                        "min": {"type": "number"},
                        "max": {"type": "number"}
                    }
                }
            }
        }
    }
}

REQUEST_SCHEMA = {
    "type": "object",
    "required": ["application", "cost_limit", "volume_kg"],
    "properties": {
        "application": {"type": "string", "minLength": 1},
        "cost_limit": {"type": "number", "minimum": 10, "maximum": 1000},
        "volume_kg": {"type": "integer", "minimum": 1, "maximum": 100000},
        "quality_target": {"type": "string"},
        "delivery_days": {"type": "integer", "minimum": 1, "maximum": 365},
        "constraints": {
            "type": "object",
            "properties": {
                "avoid_materials": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "required_materials": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "max_complexity": {"type": "integer", "minimum": 3, "maximum": 15}
            }
        },
        "semantic_preferences": {
            "type": "object",
            "properties": {
                "eco_friendly": {"type": "boolean"},
                "high_performance": {"type": "boolean"},
                "cost_optimized": {"type": "boolean"}
            }
        },
        "innovation_level": {
            "type": "string",
            "enum": ["conservative", "balanced", "high"]
        },
        "sustainability_focus": {"type": "boolean"}
    }
}


class DataValidator:
    """Comprehensive data validation for GraphRAG system."""
    
    @staticmethod
    def validate_json_schema(data: Any, schema: Dict[str, Any], data_type: str) -> List[str]:
        """Validate data against JSON schema."""
        try:
            jsonschema.validate(data, schema)
            return []
        except jsonschema.ValidationError as e:
            error_msg = f"{data_type} validation error: {e.message}"
            if e.absolute_path:
                error_msg += f" at path: {'.'.join(str(p) for p in e.absolute_path)}"
            return [error_msg]
        except Exception as e:
            return [f"{data_type} schema validation failed: {str(e)}"]
    
    @staticmethod
    def validate_formulations(formulations: List[Dict[str, Any]]) -> List[str]:
        """Validate formulations data."""
        errors = []
        
        if not isinstance(formulations, list):
            return ["Formulations must be a list"]
        
        if not formulations:
            return ["Formulations list cannot be empty"]
        
        seen_ids = set()
        
        for i, formulation in enumerate(formulations):
            # Schema validation
            schema_errors = DataValidator.validate_json_schema(
                formulation, FORMULATION_SCHEMA, f"Formulation {i}"
            )
            errors.extend(schema_errors)
            
            # Business logic validation
            fm_id = formulation.get('id', '')
            if fm_id in seen_ids:
                errors.append(f"Duplicate formulation ID: {fm_id}")
            seen_ids.add(fm_id)
            
            # Validate formulation composition
            formula = formulation.get('formula', {})
            if isinstance(formula, dict):
                total_phr = 0
                for material, phr_data in formula.items():
                    phr = phr_data.get('phr', phr_data) if isinstance(phr_data, dict) else phr_data
                    if isinstance(phr, (int, float)) and phr > 0:
                        total_phr += phr
                
                if total_phr < 50:
                    errors.append(f"Formulation {fm_id}: Total PHR too low ({total_phr})")
                elif total_phr > 200:
                    errors.append(f"Formulation {fm_id}: Total PHR too high ({total_phr})")
            
            # Validate cost reasonableness
            cost = formulation.get('cost_per_kg', 0)
            if cost > 0:
                if cost < 20:
                    errors.append(f"Formulation {fm_id}: Cost suspiciously low (₹{cost}/kg)")
                elif cost > 200:
                    errors.append(f"Formulation {fm_id}: Cost suspiciously high (₹{cost}/kg)")
        
        return errors
    
    @staticmethod
    def validate_suppliers(suppliers: List[Dict[str, Any]]) -> List[str]:
        """Validate suppliers data."""
        errors = []
        
        if not isinstance(suppliers, list):
            return ["Suppliers must be a list"]
        
        if not suppliers:
            return ["Suppliers list cannot be empty"]
        
        seen_ids = set()
        
        for i, supplier in enumerate(suppliers):
            # Schema validation
            schema_errors = DataValidator.validate_json_schema(
                supplier, SUPPLIER_SCHEMA, f"Supplier {i}"
            )
            errors.extend(schema_errors)
            
            # Business logic validation
            supplier_id = supplier.get('id', '')
            if supplier_id in seen_ids:
                errors.append(f"Duplicate supplier ID: {supplier_id}")
            seen_ids.add(supplier_id)
            
            # Validate price reasonableness
            price = supplier.get('price', 0)
            if price > 0:
                # Prices are already in ₹/kg - no conversion needed
                price_per_kg = price
                
                if price_per_kg < 10:  # Minimum realistic price ₹10/kg
                    errors.append(f"Supplier {supplier_id}: Price suspiciously low (₹{price_per_kg}/kg)")
                elif price_per_kg > 500000:  # Maximum realistic price ₹500,000/kg
                    errors.append(f"Supplier {supplier_id}: Price suspiciously high (₹{price_per_kg}/kg)")
            
            # Validate reliability score
            rel_score = supplier.get('rel_score', 0)
            if rel_score < 0 or rel_score > 5:
                errors.append(f"Supplier {supplier_id}: Invalid reliability score ({rel_score})")
        
        return errors
    
    @staticmethod
    def validate_ingredients(ingredients: Dict[str, Any]) -> List[str]:
        """Validate ingredients data."""
        errors = []
        
        if not isinstance(ingredients, dict):
            return ["Ingredients must be a dictionary"]
        
        # Schema validation
        schema_errors = DataValidator.validate_json_schema(
            ingredients, INGREDIENT_SCHEMA, "Ingredients"
        )
        errors.extend(schema_errors)
        
        # Validate required categories
        required_categories = ['PVC_RESINS', 'PLASTICIZERS', 'FILLERS', 'STABILIZERS']
        for category in required_categories:
            if category not in ingredients:
                errors.append(f"Missing required ingredient category: {category}")
            elif not isinstance(ingredients[category], list) or not ingredients[category]:
                errors.append(f"Ingredient category {category} must be a non-empty list")
        
        # Validate individual ingredients
        all_ingredient_ids = set()
        
        for category, items in ingredients.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        ingredient_id = item.get('id', '')
                        if ingredient_id in all_ingredient_ids:
                            errors.append(f"Duplicate ingredient ID: {ingredient_id}")
                        all_ingredient_ids.add(ingredient_id)
                        
                        # Validate cost
                        cost = item.get('cost_per_kg', 0)
                        if cost <= 0:
                            errors.append(f"Ingredient {ingredient_id}: Invalid cost ({cost})")
        
        return errors
    
    @staticmethod
    def validate_standards(standards: Dict[str, Any]) -> List[str]:
        """Validate compliance standards data."""
        errors = []
        
        if not isinstance(standards, dict):
            return ["Standards must be a dictionary"]
        
        # Schema validation
        schema_errors = DataValidator.validate_json_schema(
            standards, STANDARDS_SCHEMA, "Standards"
        )
        errors.extend(schema_errors)
        
        # Validate required standards
        required_standards = ['IS_5831']
        for std in required_standards:
            if std not in standards:
                errors.append(f"Missing required standard: {std}")
        
        # Validate standard requirements
        for std_id, requirements in standards.items():
            if isinstance(requirements, dict):
                for prop, limits in requirements.items():
                    if isinstance(limits, dict):
                        min_val = limits.get('min')
                        max_val = limits.get('max')
                        
                        if min_val is not None and max_val is not None:
                            if min_val >= max_val:
                                errors.append(f"Standard {std_id}.{prop}: min ({min_val}) >= max ({max_val})")
        
        return errors
    
    @staticmethod
    def validate_all_databases(db_files: Dict[str, Path]) -> List[str]:
        """Validate all database files."""
        all_errors = []
        
        try:
            # Validate formulations
            if 'formulations' in db_files:
                with open(db_files['formulations'], 'r', encoding='utf-8') as f:
                    formulations_data = json.load(f)
                
                if isinstance(formulations_data, list):
                    formulations = formulations_data
                elif isinstance(formulations_data, dict) and 'formulations' in formulations_data:
                    formulations = formulations_data['formulations']
                else:
                    all_errors.append("Invalid formulations file structure")
                    formulations = []
                
                errors = DataValidator.validate_formulations(formulations)
                all_errors.extend([f"Formulations: {e}" for e in errors])
            
            # Validate suppliers
            if 'suppliers' in db_files:
                with open(db_files['suppliers'], 'r', encoding='utf-8') as f:
                    suppliers = json.load(f)
                
                errors = DataValidator.validate_suppliers(suppliers)
                all_errors.extend([f"Suppliers: {e}" for e in errors])
            
            # Validate ingredients
            if 'ingredients' in db_files:
                with open(db_files['ingredients'], 'r', encoding='utf-8') as f:
                    ingredients = json.load(f)
                
                errors = DataValidator.validate_ingredients(ingredients)
                all_errors.extend([f"Ingredients: {e}" for e in errors])
            
            # Validate standards
            if 'standards' in db_files:
                with open(db_files['standards'], 'r', encoding='utf-8') as f:
                    standards = json.load(f)
                
                errors = DataValidator.validate_standards(standards)
                all_errors.extend([f"Standards: {e}" for e in errors])
        
        except FileNotFoundError as e:
            all_errors.append(f"Database file not found: {e}")
        except json.JSONDecodeError as e:
            all_errors.append(f"JSON parsing error: {e}")
        except Exception as e:
            all_errors.append(f"Database validation error: {e}")
        
        return all_errors
    
    @staticmethod
    def check_data_consistency(formulations: List[Dict[str, Any]], 
                             suppliers: List[Dict[str, Any]], 
                             ingredients: Dict[str, Any]) -> List[str]:
        """Check consistency across databases."""
        issues = []
        
        try:
            # Collect all materials from formulations
            formulation_materials = set()
            for fm in formulations:
                formula = fm.get('formula', fm.get('formulation', {}))
                if isinstance(formula, dict):
                    formulation_materials.update(formula.keys())
            
            # Collect all materials from suppliers
            supplier_materials = set()
            for supplier in suppliers:
                product = supplier.get('prod', supplier.get('product', ''))
                if product:
                    supplier_materials.add(product)
            
            # Collect all materials from ingredients
            ingredient_materials = set()
            if isinstance(ingredients, dict):
                for category, items in ingredients.items():
                    if isinstance(items, list):
                        for item in items:
                            if isinstance(item, dict):
                                ingredient_id = item.get('id', '')
                                if ingredient_id:
                                    ingredient_materials.add(ingredient_id)
            
            # Check for materials in formulations but not in suppliers
            missing_suppliers = formulation_materials - supplier_materials
            if missing_suppliers:
                issues.append(f"Materials in formulations but no suppliers: {missing_suppliers}")
            
            # Check for materials in formulations but not in ingredients
            missing_ingredients = formulation_materials - ingredient_materials
            if missing_ingredients:
                issues.append(f"Materials in formulations but not in ingredients: {missing_ingredients}")
            
            # Check for suppliers without corresponding ingredients
            orphaned_suppliers = supplier_materials - ingredient_materials
            if orphaned_suppliers:
                issues.append(f"Suppliers for materials not in ingredients: {orphaned_suppliers}")
        
        except Exception as e:
            issues.append(f"Consistency check failed: {e}")
        
        return issues


class RequestValidator:
    """Validate and sanitize user requests."""
    
    @staticmethod
    def validate_request(request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize user request."""
        if not isinstance(request, dict):
            raise ValidationError("Request must be a dictionary")
        
        # Schema validation
        schema_errors = DataValidator.validate_json_schema(
            request, REQUEST_SCHEMA, "Request"
        )
        
        if schema_errors:
            raise ValidationError(f"Request validation failed: {'; '.join(schema_errors)}")
        
        # Create validated copy
        validated = {}
        
        # Required fields with validation
        validated['application'] = RequestValidator._validate_application(
            request.get('application', '')
        )
        validated['cost_limit'] = RequestValidator._validate_cost_limit(
            request.get('cost_limit', 0)
        )
        validated['volume_kg'] = RequestValidator._validate_volume(
            request.get('volume_kg', 0)
        )
        
        # Optional fields with defaults
        validated['quality_target'] = RequestValidator._validate_quality_target(
            request.get('quality_target', 'IS_5831')
        )
        validated['delivery_days'] = RequestValidator._validate_delivery_days(
            request.get('delivery_days', Config.DEFAULT_DELIVERY_DAYS)
        )
        
        # Complex optional fields
        validated['constraints'] = RequestValidator._validate_constraints(
            request.get('constraints', {})
        )
        validated['semantic_preferences'] = RequestValidator._validate_semantic_preferences(
            request.get('semantic_preferences', {})
        )
        validated['innovation_level'] = request.get('innovation_level', 'balanced')
        validated['sustainability_focus'] = bool(request.get('sustainability_focus', False))
        
        return validated
    
    @staticmethod
    def _validate_application(application: str) -> str:
        """Validate application field."""
        if not isinstance(application, str) or not application.strip():
            raise ValidationError("Application must be a non-empty string")
        
        # Normalize application name
        app_lower = application.lower().strip()
        
        # Map common variations to standard names
        app_mapping = {
            'cable': 'cable_insulation_low_voltage',
            'cable insulation': 'cable_insulation_low_voltage',
            'wire': 'cable_insulation_low_voltage',
            'electrical': 'cable_insulation_low_voltage',
            'pipe': 'pvc_pipe_compound',
            'plumbing': 'pvc_pipe_compound',
            'film': 'pvc_film_grade',
            'sheet': 'pvc_film_grade',
            'profile': 'pvc_profile_compound',
            'window': 'pvc_profile_compound',
            'door': 'pvc_profile_compound'
        }
        
        return app_mapping.get(app_lower, application.strip())
    
    @staticmethod
    def _validate_cost_limit(cost_limit: Union[str, int, float]) -> float:
        """Validate cost limit field."""
        try:
            cost = float(cost_limit)
        except (ValueError, TypeError):
            raise ValidationError(f"Cost limit must be a number, got: {cost_limit}")
        
        if cost <= 0:
            raise ValidationError(f"Cost limit must be positive, got: {cost}")
        
        if cost < 10:
            raise ValidationError(f"Cost limit too low (minimum ₹10/kg), got: ₹{cost}/kg")
        
        if cost > 1000:
            raise ValidationError(f"Cost limit too high (maximum ₹1000/kg), got: ₹{cost}/kg")
        
        return cost
    
    @staticmethod
    def _validate_volume(volume: Union[str, int, float]) -> int:
        """Validate volume field."""
        try:
            vol = int(float(volume))
        except (ValueError, TypeError):
            raise ValidationError(f"Volume must be a number, got: {volume}")
        
        if vol <= 0:
            raise ValidationError(f"Volume must be positive, got: {vol}")
        
        if vol > 100000:
            raise ValidationError(f"Volume too large (maximum 100,000 kg), got: {vol} kg")
        
        return vol
    
    @staticmethod
    def _validate_quality_target(quality_target: str) -> str:
        """Validate quality target field."""
        if not isinstance(quality_target, str):
            raise ValidationError("Quality target must be a string")
        
        # Normalize standard names
        std_mapping = {
            'is5831': 'IS_5831',
            'is_5831': 'IS_5831',
            'is 5831': 'IS_5831',
            'rohs': 'RoHS',
            'reach': 'REACH'
        }
        
        normalized = std_mapping.get(quality_target.lower(), quality_target)
        
        return normalized
    
    @staticmethod
    def _validate_delivery_days(delivery_days: Union[str, int, float]) -> int:
        """Validate delivery days field."""
        try:
            days = int(float(delivery_days))
        except (ValueError, TypeError):
            raise ValidationError(f"Delivery days must be a number, got: {delivery_days}")
        
        if days <= 0:
            raise ValidationError(f"Delivery days must be positive, got: {days}")
        
        if days > 365:
            raise ValidationError(f"Delivery days too long (maximum 365), got: {days}")
        
        return days
    
    @staticmethod
    def _validate_constraints(constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Validate constraints field."""
        if not isinstance(constraints, dict):
            return {}
        
        validated_constraints = {}
        
        # Validate avoid_materials
        avoid_materials = constraints.get('avoid_materials', [])
        if isinstance(avoid_materials, list):
            validated_constraints['avoid_materials'] = [
                str(material).strip() for material in avoid_materials 
                if str(material).strip()
            ]
        else:
            validated_constraints['avoid_materials'] = []
        
        # Validate required_materials
        required_materials = constraints.get('required_materials', [])
        if isinstance(required_materials, list):
            validated_constraints['required_materials'] = [
                str(material).strip() for material in required_materials 
                if str(material).strip()
            ]
        else:
            validated_constraints['required_materials'] = []
        
        # Validate max_complexity
        max_complexity = constraints.get('max_complexity')
        if max_complexity is not None:
            try:
                complexity = int(max_complexity)
                if 3 <= complexity <= 15:
                    validated_constraints['max_complexity'] = complexity
            except (ValueError, TypeError):
                pass
        
        return validated_constraints
    
    @staticmethod
    def _validate_semantic_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Validate semantic preferences field."""
        if not isinstance(preferences, dict):
            return {}
        
        validated_prefs = {}
        
        # Boolean preferences
        bool_prefs = ['eco_friendly', 'high_performance', 'cost_optimized']
        for pref in bool_prefs:
            if pref in preferences:
                validated_prefs[pref] = bool(preferences[pref])
        
        return validated_prefs


class PropertyValidator:
    """Validate material properties and predictions."""
    
    @staticmethod
    def validate_properties(properties: Dict[str, Any]) -> List[str]:
        """Validate material properties."""
        issues = []
        
        if not isinstance(properties, dict):
            return ["Properties must be a dictionary"]
        
        # Define property ranges
        property_ranges = {
            'tensile_strength_mpa': (5.0, 50.0),
            'elongation_percent': (50.0, 500.0),
            'hardness_shore': (30.0, 100.0),
            'brittleness_temp_c': (-50.0, 10.0),
            'viscosity_cps': (200.0, 2000.0)
        }
        
        for prop, value in properties.items():
            if isinstance(value, (int, float)):
                if prop in property_ranges:
                    min_val, max_val = property_ranges[prop]
                    if value < min_val or value > max_val:
                        issues.append(f"{prop}: {value} outside valid range ({min_val}-{max_val})")
                elif prop.endswith('_mpa') and (value < 0 or value > 100):
                    issues.append(f"{prop}: {value} MPa outside reasonable range (0-100)")
                elif prop.endswith('_percent') and (value < 0 or value > 1000):
                    issues.append(f"{prop}: {value}% outside reasonable range (0-1000)")
                elif prop.endswith('_shore') and (value < 0 or value > 100):
                    issues.append(f"{prop}: {value} Shore outside valid range (0-100)")
        
        return issues
    
    @staticmethod
    def validate_property_consistency(properties: Dict[str, Any]) -> List[str]:
        """Validate consistency between related properties."""
        issues = []
        
        # Check tensile strength vs elongation relationship
        tensile = properties.get('tensile_strength_mpa')
        elongation = properties.get('elongation_percent')
        
        if tensile and elongation:
            # Generally, higher tensile strength correlates with lower elongation
            if tensile > 25 and elongation > 300:
                issues.append("High tensile strength with high elongation is unusual")
            elif tensile < 12 and elongation < 150:
                issues.append("Low tensile strength with low elongation indicates poor formulation")
        
        # Check hardness vs elongation relationship
        hardness = properties.get('hardness_shore')
        
        if hardness and elongation:
            # Higher hardness typically means lower elongation
            if hardness > 85 and elongation > 250:
                issues.append("High hardness with high elongation is inconsistent")
        
        return issues


class GraphRAGValidator:
    """Specialized validator for GraphRAG operations."""
    
    @staticmethod
    def validate_semantic_query(query: str) -> List[str]:
        """Validate semantic search query."""
        issues = []
        
        if not isinstance(query, str):
            issues.append("Query must be a string")
            return issues
        
        query = query.strip()
        
        if not query:
            issues.append("Query cannot be empty")
        elif len(query) < 3:
            issues.append("Query too short (minimum 3 characters)")
        elif len(query) > 1000:
            issues.append("Query too long (maximum 1000 characters)")
        
        # Check for potentially problematic characters
        if re.search(r'[<>{}[\]\\]', query):
            issues.append("Query contains potentially unsafe characters")
        
        return issues
    
    @staticmethod
    def validate_graph_traversal_params(max_depth: int, similarity_threshold: float) -> List[str]:
        """Validate graph traversal parameters."""
        issues = []
        
        if not isinstance(max_depth, int) or max_depth < 1 or max_depth > 10:
            issues.append("Max depth must be an integer between 1 and 10")
        
        if not isinstance(similarity_threshold, (int, float)) or similarity_threshold < 0 or similarity_threshold > 1:
            issues.append("Similarity threshold must be a number between 0 and 1")
        
        return issues
    
    @staticmethod
    def validate_embedding_dimensions(dimensions: int) -> List[str]:
        """Validate embedding dimensions."""
        issues = []
        
        if not isinstance(dimensions, int):
            issues.append("Embedding dimensions must be an integer")
        elif dimensions < 10:
            issues.append("Embedding dimensions too low (minimum 10)")
        elif dimensions > 1000:
            issues.append("Embedding dimensions too high (maximum 1000)")
        
        return issues