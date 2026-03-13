"""Input validation and data schemas for RND Agent."""

import json
import jsonschema
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from .exceptions import ValidationError, DataValidationError
from .logging_config import get_logger

logger = get_logger(__name__)


# JSON Schemas for data validation
FORMULATION_SCHEMA = {
    "type": "object",
    "required": ["id", "app", "formula", "cost_per_kg", "prop"],
    "properties": {
        "id": {"type": "string", "pattern": "^FM-\\d{4}$"},
        "date": {"type": "string", "format": "date"},
        "app": {"type": "string", "minLength": 1},
        "std": {"type": "string"},
        "cust": {"type": "string"},
        "vol_kg": {"type": "number", "minimum": 1},
        "formula": {
            "type": "object",
            "patternProperties": {
                "^[A-Za-z0-9_]+$": {"type": "number", "minimum": 0}
            }
        },
        "cost_per_kg": {"type": "number", "minimum": 0},
        "prop": {
            "type": "object",
            "properties": {
                "tens_mpa": {"type": "number", "minimum": 0},
                "elong_pct": {"type": "number", "minimum": 0},
                "hard_shore": {"type": "number", "minimum": 0, "maximum": 100},
                "brit_temp_c": {"type": "number"},
                "visc_cps": {"type": "number", "minimum": 0}
            },
            "required": ["tens_mpa", "elong_pct", "hard_shore"]
        },
        "verdict": {"type": "string", "enum": ["PASS", "FAIL", "UNKNOWN"]},
        "yield": {"type": "number", "minimum": 0, "maximum": 100},
        "notes": {"type": "string"}
    }
}

SUPPLIER_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "loc", "price", "avail"],
    "properties": {
        "id": {"type": "string", "pattern": "^SUPP-\\d{4}$"},
        "name": {"type": "string", "minLength": 1},
        "loc": {"type": "string", "minLength": 1},
        "prod": {"type": "string"},
        "price": {"type": "number", "minimum": 0},
        "min_ord": {"type": "number", "minimum": 0},
        "lead_d": {"type": "number", "minimum": 0},
        "rel_score": {"type": "number", "minimum": 0, "maximum": 5},
        "cert": {"type": "string"},
        "month": {"type": "string"},
        "avail": {"type": "string", "enum": ["Yes", "Limited", "No"]}
    }
}

INGREDIENT_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^[A-Za-z_]+$": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "name", "price_per_kg", "properties"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string", "minLength": 1},
                    "price_per_kg": {"type": "number", "minimum": 0},
                    "supplier": {"type": "string"},
                    "properties": {"type": "object"},
                    "compliance": {"type": "object"}
                }
            }
        }
    }
}

REQUEST_SCHEMA = {
    "type": "object",
    "required": ["application"],
    "properties": {
        "application": {"type": "string", "minLength": 1},
        "cost_limit": {"type": "number", "minimum": 1},
        "volume_kg": {"type": "number", "minimum": 1},
        "quality_target": {"type": "string"},
        "delivery_days": {"type": "number", "minimum": 1},
        "constraints": {
            "type": "object",
            "properties": {
                "avoid_materials": {"type": "array", "items": {"type": "string"}},
                "required_materials": {"type": "array", "items": {"type": "string"}},
                "max_hardness": {"type": "number"},
                "min_tensile": {"type": "number"},
                "min_elongation": {"type": "number"}
            }
        }
    }
}


class RequestValidator:
    """Validates and sanitizes user requests."""
    
    @staticmethod
    def validate_request(request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize user request."""
        if not request or not isinstance(request, dict):
            raise ValidationError("Request must be non-empty dictionary")
        
        try:
            # Validate against schema
            jsonschema.validate(request, REQUEST_SCHEMA)
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Request validation failed: {e.message}")
        
        # Sanitize and set defaults
        sanitized = {
            'application': str(request['application']).lower().strip(),
            'cost_limit': float(request.get('cost_limit', 70.0)),
            'volume_kg': int(request.get('volume_kg', 100)),
            'quality_target': str(request.get('quality_target', 'IS_5831')).upper(),
            'delivery_days': int(request.get('delivery_days', 10)),
            'constraints': request.get('constraints', {})
        }
        
        # Validate ranges
        if sanitized['cost_limit'] <= 0:
            raise ValidationError(f"Cost limit must be positive: {sanitized['cost_limit']}")
        
        if sanitized['volume_kg'] <= 0:
            raise ValidationError(f"Volume must be positive: {sanitized['volume_kg']}")
        
        if sanitized['delivery_days'] <= 0:
            raise ValidationError(f"Delivery days must be positive: {sanitized['delivery_days']}")
        
        if not sanitized['application']:
            raise ValidationError("Application cannot be empty")
        
        logger.debug(f"Request validated: {sanitized}")
        return sanitized
    
    @staticmethod
    def validate_formulation(formulation: Dict[str, Any]) -> bool:
        """Validate formulation structure."""
        if not isinstance(formulation, dict):
            return False
        
        if 'ingredients' not in formulation:
            return False
        
        ingredients = formulation['ingredients']
        if not isinstance(ingredients, dict) or not ingredients:
            return False
        
        # Check PHR values
        for material, data in ingredients.items():
            if isinstance(data, dict):
                phr = data.get('phr', 0)
            else:
                phr = data
            
            if not isinstance(phr, (int, float)) or phr < 0:
                return False
        
        return True


class DataValidator:
    """Validates database files and data integrity."""
    
    @staticmethod
    def validate_json_file(filepath: Path, schema: Dict[str, Any]) -> None:
        """Validate JSON file against schema."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise DataValidationError(f"Failed to load {filepath}: {e}")
        
        try:
            if isinstance(data, list):
                for i, item in enumerate(data):
                    try:
                        jsonschema.validate(item, schema)
                    except jsonschema.ValidationError as e:
                        raise DataValidationError(
                            f"Validation failed for item {i} in {filepath}: {e.message}"
                        )
            else:
                jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            raise DataValidationError(f"Schema validation failed for {filepath}: {e.message}")
        
        logger.info(f"Data validation passed: {filepath}")
    
    @staticmethod
    def validate_all_databases(db_files: Dict[str, Path]) -> None:
        """Validate all database files."""
        validations = [
            ('formulations', FORMULATION_SCHEMA),
            ('suppliers', SUPPLIER_SCHEMA),
            ('ingredients', INGREDIENT_SCHEMA)
        ]
        
        for db_name, schema in validations:
            if db_name in db_files:
                try:
                    DataValidator.validate_json_file(db_files[db_name], schema)
                except DataValidationError as e:
                    logger.warning(f"Validation failed for {db_name}: {e}")
                    # Continue with other validations
        
        logger.info("Database validation completed")
    
    @staticmethod
    def check_data_consistency(formulations: List[Dict], suppliers: List[Dict], ingredients: Dict) -> List[str]:
        """Check cross-database data consistency."""
        issues = []
        
        # Check if all formulation materials have suppliers
        all_materials = set()
        for fm in formulations:
            formula = fm.get('formula', fm.get('formulation', {}))
            if isinstance(formula, dict):
                all_materials.update(formula.keys())
        
        # Build supplier materials set
        supplier_materials = set()
        if isinstance(suppliers, list):
            for supplier in suppliers:
                product = supplier.get('product', supplier.get('prod', ''))
                if product:
                    supplier_materials.add(product)
        elif isinstance(suppliers, dict):
            supplier_materials = set(suppliers.keys())
        
        missing_suppliers = all_materials - supplier_materials
        if missing_suppliers:
            issues.append(f"Materials without suppliers: {missing_suppliers}")
        
        # Check if all materials have ingredient data
        ingredient_materials = set()
        if isinstance(ingredients, dict):
            for category in ingredients.values():
                if isinstance(category, list):
                    for item in category:
                        if 'id' in item:
                            ingredient_materials.add(item['id'])
        
        missing_ingredients = all_materials - ingredient_materials
        if missing_ingredients:
            issues.append(f"Materials without ingredient data: {missing_ingredients}")
        
        if issues:
            logger.warning(f"Data consistency issues found: {issues}")
        else:
            logger.info("Data consistency check passed")
        
        return issues


class PropertyValidator:
    """Validates material properties and predictions."""
    
    @staticmethod
    def validate_properties(properties: Dict[str, float]) -> Dict[str, str]:
        """Validate material properties against industry standards."""
        issues = {}
        
        # Tensile strength validation
        tensile = properties.get('tensile_strength_mpa', 0)
        if tensile < 10:
            issues['tensile_strength'] = f"Too low: {tensile} MPa (min: 10 MPa)"
        elif tensile > 50:
            issues['tensile_strength'] = f"Unusually high: {tensile} MPa (typical max: 50 MPa)"
        
        # Elongation validation
        elongation = properties.get('elongation_percent', 0)
        if elongation < 100:
            issues['elongation'] = f"Too low: {elongation}% (min: 100%)"
        elif elongation > 500:
            issues['elongation'] = f"Unusually high: {elongation}% (typical max: 500%)"
        
        # Hardness validation
        hardness = properties.get('hardness_shore', 0)
        if hardness < 40:
            issues['hardness'] = f"Too soft: {hardness} Shore A (min: 40)"
        elif hardness > 95:
            issues['hardness'] = f"Too hard: {hardness} Shore A (max: 95)"
        
        return issues