"""Production data layer for GraphRAG Agent with advanced caching and indexing."""

import json
import pickle
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from functools import lru_cache
from collections import defaultdict
import hashlib

from config import Config
from exceptions import DatabaseError, DataValidationError, ExceptionHandler
from formulation_validators import DataValidator
from logging_config import get_logger, PerformanceLogger

logger = get_logger(__name__)
perf_logger = PerformanceLogger(__name__)


class AdvancedDataLoader:
    """Thread-safe advanced data loader with intelligent caching and validation."""
    
    _instance: Optional['AdvancedDataLoader'] = None
    _lock = threading.RLock()
    
    def __new__(cls) -> 'AdvancedDataLoader':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self.db_files = Config.get_database_files()
        self._data_cache: Dict[str, Any] = {}
        self._file_hashes: Dict[str, str] = {}
        self._cache_file = Path('graphrag_data_cache.pkl')
        self._last_validation_time: Optional[float] = None
        self._validation_interval = 3600  # 1 hour
        self._initialized = True
        
        logger.info("Advanced DataLoader initialized")
    
    @ExceptionHandler.handle_exceptions
    def load_all_databases(self, force_reload: bool = False) -> Dict[str, Any]:
        """Load and validate all databases with intelligent caching."""
        with self._lock:
            try:
                with perf_logger.timer("database_loading"):
                    # Check if we need to reload
                    if not force_reload and self._is_cache_valid():
                        logger.info("Using cached database data")
                        return self._data_cache.copy()
                    
                    # Load from files
                    data = self._load_from_files()
                    
                    # Validate data integrity
                    self._validate_data_integrity(data)
                    
                    # Update cache
                    self._update_cache(data)
                    
                    # Update file hashes
                    self._update_file_hashes()
                    
                    logger.info("Database loading completed successfully")
                    return data
                    
            except Exception as e:
                logger.error(f"Database loading failed: {e}")
                raise DatabaseError(f"Failed to load databases: {e}")
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid."""
        try:
            # Check if cache exists
            if not self._data_cache:
                return False
            
            # Check file modification times
            for db_name, file_path in self.db_files.items():
                if not file_path.exists():
                    return False
                
                # Calculate current file hash
                current_hash = self._calculate_file_hash(file_path)
                cached_hash = self._file_hashes.get(db_name)
                
                if current_hash != cached_hash:
                    logger.info(f"File {db_name} has changed, cache invalid")
                    return False
            
            # Check validation interval
            current_time = time.time()
            if (self._last_validation_time is None or 
                current_time - self._last_validation_time > self._validation_interval):
                logger.info("Cache validation interval exceeded")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Cache validation failed: {e}")
            return False
    
    def _load_from_files(self) -> Dict[str, Any]:
        """Load all database files with comprehensive error handling."""
        logger.info("Loading databases from files")
        
        data = {}
        
        # Load each database file
        for db_name, file_path in self.db_files.items():
            try:
                with perf_logger.timer(f"load_{db_name}"):
                    loaded_data = self._load_json_file(file_path, db_name)
                    data[db_name] = loaded_data
                    logger.debug(f"Loaded {db_name}: {self._get_data_summary(loaded_data)}")
                    
            except Exception as e:
                logger.error(f"Failed to load {db_name} from {file_path}: {e}")
                raise DatabaseError(f"Failed to load {db_name}: {e}")
        
        return data
    
    def _load_json_file(self, file_path: Path, db_name: str) -> Any:
        """Load and parse JSON file with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different data structures
            if db_name == 'formulations':
                # Handle both list and dict formats
                if isinstance(data, dict) and 'formulations' in data:
                    return data['formulations']
                elif isinstance(data, list):
                    return data
                else:
                    raise DatabaseError(f"Invalid formulations structure in {file_path}")
            
            return data
            
        except FileNotFoundError:
            raise DatabaseError(f"Database file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise DatabaseError(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            raise DatabaseError(f"Failed to load {file_path}: {e}")
    
    def _validate_data_integrity(self, data: Dict[str, Any]) -> None:
        """Validate data integrity and consistency."""
        try:
            with perf_logger.timer("data_validation"):
                # Validate individual databases
                validation_errors = []
                
                if 'formulations' in data:
                    errors = DataValidator.validate_formulations(data['formulations'])
                    validation_errors.extend([f"Formulations: {e}" for e in errors])
                
                if 'suppliers' in data:
                    errors = DataValidator.validate_suppliers(data['suppliers'])
                    validation_errors.extend([f"Suppliers: {e}" for e in errors])
                
                if 'ingredients' in data:
                    errors = DataValidator.validate_ingredients(data['ingredients'])
                    validation_errors.extend([f"Ingredients: {e}" for e in errors])
                
                if 'standards' in data:
                    errors = DataValidator.validate_standards(data['standards'])
                    validation_errors.extend([f"Standards: {e}" for e in errors])
                
                # Check cross-database consistency
                if 'formulations' in data and 'suppliers' in data and 'ingredients' in data:
                    consistency_errors = DataValidator.check_data_consistency(
                        data['formulations'], data['suppliers'], data['ingredients']
                    )
                    validation_errors.extend([f"Consistency: {e}" for e in consistency_errors])
                
                # Log validation results
                if validation_errors:
                    logger.warning(f"Data validation issues found: {len(validation_errors)} issues")
                    for error in validation_errors[:10]:  # Log first 10 errors
                        logger.warning(f"Validation: {error}")
                    
                    # Don't fail on validation warnings, just log them
                    if len(validation_errors) > 50:
                        raise DataValidationError(f"Too many validation errors: {len(validation_errors)}")
                else:
                    logger.info("Data validation passed")
                
                self._last_validation_time = time.time()
                
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            raise DataValidationError(f"Data validation failed: {e}")
    
    def _update_cache(self, data: Dict[str, Any]) -> None:
        """Update internal cache with new data."""
        try:
            self._data_cache = data.copy()
            
            # Save to disk cache
            cache_data = {
                'timestamp': time.time(),
                'data': data,
                'file_hashes': self._file_hashes.copy()
            }
            
            with open(self._cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.debug("Data cache updated")
            
        except Exception as e:
            logger.warning(f"Failed to update cache: {e}")
    
    def _update_file_hashes(self) -> None:
        """Update file hashes for change detection."""
        try:
            for db_name, file_path in self.db_files.items():
                if file_path.exists():
                    self._file_hashes[db_name] = self._calculate_file_hash(file_path)
        except Exception as e:
            logger.warning(f"Failed to update file hashes: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return str(file_path.stat().st_mtime)  # Fallback to modification time
    
    def _get_data_summary(self, data: Any) -> str:
        """Get summary of loaded data."""
        if isinstance(data, list):
            return f"{len(data)} items"
        elif isinstance(data, dict):
            return f"{len(data)} keys"
        else:
            return f"type: {type(data).__name__}"
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self._data_cache),
            'file_hashes_count': len(self._file_hashes),
            'last_validation_time': self._last_validation_time,
            'cache_file_exists': self._cache_file.exists(),
            'cache_file_size': self._cache_file.stat().st_size if self._cache_file.exists() else 0
        }


class AdvancedFormulationIndex:
    """Advanced indexing system for formulation search with multiple access patterns."""
    
    def __init__(self, formulations: List[Dict[str, Any]]):
        self.formulations = formulations
        self._build_comprehensive_indexes()
    
    def _build_comprehensive_indexes(self) -> None:
        """Build comprehensive search indexes."""
        logger.info("Building advanced formulation indexes")
        
        with perf_logger.timer("formulation_indexing"):
            # Basic indexes
            self.by_id: Dict[str, Dict[str, Any]] = {}
            self.by_application: Dict[str, List[Dict]] = defaultdict(list)
            self.by_cost_range: Dict[Tuple[int, int], List[Dict]] = defaultdict(list)
            self.by_material: Dict[str, List[Dict]] = defaultdict(list)
            self.by_compliance: Dict[str, List[Dict]] = defaultdict(list)
            
            # Advanced indexes
            self.by_property_range: Dict[str, Dict[Tuple[float, float], List[Dict]]] = defaultdict(lambda: defaultdict(list))
            self.by_material_combination: Dict[frozenset, List[Dict]] = defaultdict(list)
            self.by_complexity: Dict[int, List[Dict]] = defaultdict(list)
            
            # Performance indexes
            self.high_performance: List[Dict] = []
            self.cost_optimized: List[Dict] = []
            self.eco_friendly: List[Dict] = []
            
            for fm in self.formulations:
                self._index_formulation(fm)
            
            logger.info(f"Built indexes: {len(self.by_application)} applications, "
                       f"{len(self.by_cost_range)} cost ranges, "
                       f"{len(self.by_material)} materials")
    
    def _index_formulation(self, fm: Dict[str, Any]) -> None:
        """Index a single formulation across all indexes."""
        fm_id = fm.get('id', '')
        
        # ID index
        if fm_id:
            self.by_id[fm_id] = fm
        
        # Application index
        app = fm.get('app', fm.get('application', '')).lower()
        if app:
            self.by_application[app].append(fm)
        
        # Cost range index (₹10 buckets)
        cost = fm.get('cost_per_kg', 0)
        if cost > 0:
            bucket = (int(cost // 10) * 10, int(cost // 10) * 10 + 10)
            self.by_cost_range[bucket].append(fm)
        
        # Material indexes
        formulation = fm.get('formula', fm.get('formulation', {}))
        if isinstance(formulation, dict):
            materials = set(formulation.keys())
            
            # Individual material index
            for material in materials:
                self.by_material[material].append(fm)
            
            # Material combination index
            if len(materials) >= 2:
                self.by_material_combination[frozenset(materials)].append(fm)
            
            # Complexity index
            complexity = len(materials)
            self.by_complexity[complexity].append(fm)
        
        # Compliance index
        verdict = fm.get('verdict', fm.get('compliance_verdict', ''))
        if verdict:
            self.by_compliance[verdict].append(fm)
        
        # Property range indexes
        properties = fm.get('prop', fm.get('properties', {}))
        if isinstance(properties, dict):
            for prop_name, prop_value in properties.items():
                if isinstance(prop_value, (int, float)):
                    # Create range buckets for properties
                    if 'tens' in prop_name.lower():
                        bucket = (int(prop_value // 5) * 5, int(prop_value // 5) * 5 + 5)
                        self.by_property_range['tensile_strength'][bucket].append(fm)
                    elif 'elong' in prop_name.lower():
                        bucket = (int(prop_value // 50) * 50, int(prop_value // 50) * 50 + 50)
                        self.by_property_range['elongation'][bucket].append(fm)
                    elif 'hard' in prop_name.lower():
                        bucket = (int(prop_value // 10) * 10, int(prop_value // 10) * 10 + 10)
                        self.by_property_range['hardness'][bucket].append(fm)
        
        # Performance category indexes
        if self._is_high_performance(fm):
            self.high_performance.append(fm)
        
        if self._is_cost_optimized(fm):
            self.cost_optimized.append(fm)
        
        if self._is_eco_friendly(fm):
            self.eco_friendly.append(fm)
    
    def _is_high_performance(self, fm: Dict[str, Any]) -> bool:
        """Check if formulation is high performance."""
        properties = fm.get('prop', fm.get('properties', {}))
        if not isinstance(properties, dict):
            return False
        
        # High performance criteria
        tensile = properties.get('tens_mpa', properties.get('tensile_strength_mpa', 0))
        elongation = properties.get('elong_pct', properties.get('elongation_percent', 0))
        
        return (tensile > 20 and elongation > 200) or fm.get('verdict') == 'PASS'
    
    def _is_cost_optimized(self, fm: Dict[str, Any]) -> bool:
        """Check if formulation is cost optimized."""
        cost = fm.get('cost_per_kg', 0)
        return cost > 0 and cost < 60
    
    def _is_eco_friendly(self, fm: Dict[str, Any]) -> bool:
        """Check if formulation is eco-friendly."""
        formulation = fm.get('formula', fm.get('formulation', {}))
        if not isinstance(formulation, dict):
            return False
        
        # Check for eco-friendly materials
        eco_materials = ['DOTP', 'DINP', 'Ca_Zn']
        non_eco_materials = ['DOP', 'DBP', 'Ba_Zn', 'Pb']
        
        has_eco = any(mat in formulation for mat in eco_materials)
        has_non_eco = any(mat in formulation for mat in non_eco_materials)
        
        return has_eco and not has_non_eco
    
    @lru_cache(maxsize=1000)
    def find_by_application(self, application: str) -> List[Dict[str, Any]]:
        """Find formulations by application with caching."""
        app_lower = application.lower()
        
        # Exact match first
        if app_lower in self.by_application:
            return self.by_application[app_lower].copy()
        
        # Partial match
        matches = []
        for app, formulations in self.by_application.items():
            if any(word in app for word in app_lower.split()):
                matches.extend(formulations)
        
        return matches
    
    @lru_cache(maxsize=500)
    def find_by_cost_range(self, min_cost: float, max_cost: float) -> List[Dict[str, Any]]:
        """Find formulations within cost range with caching."""
        matches = []
        
        for (bucket_min, bucket_max), formulations in self.by_cost_range.items():
            if bucket_max >= min_cost and bucket_min <= max_cost:
                for fm in formulations:
                    cost = fm.get('cost_per_kg', 0)
                    if min_cost <= cost <= max_cost:
                        matches.append(fm)
        
        return matches
    
    def find_by_materials(self, materials: List[str], match_type: str = 'any') -> List[Dict[str, Any]]:
        """Find formulations containing specific materials."""
        if match_type == 'all':
            # Find formulations containing all materials
            material_set = set(materials)
            matches = []
            
            for material_combo, formulations in self.by_material_combination.items():
                if material_set.issubset(material_combo):
                    matches.extend(formulations)
            
            return matches
        
        else:  # match_type == 'any'
            # Find formulations containing any of the materials
            matches = set()
            
            for material in materials:
                if material in self.by_material:
                    matches.update(self.by_material[material])
            
            return list(matches)
    
    def find_by_property_range(self, property_name: str, min_val: float, max_val: float) -> List[Dict[str, Any]]:
        """Find formulations within property range."""
        if property_name not in self.by_property_range:
            return []
        
        matches = []
        property_index = self.by_property_range[property_name]
        
        for (bucket_min, bucket_max), formulations in property_index.items():
            if bucket_max >= min_val and bucket_min <= max_val:
                for fm in formulations:
                    properties = fm.get('prop', fm.get('properties', {}))
                    if isinstance(properties, dict):
                        # Find the actual property value
                        prop_value = None
                        for key, value in properties.items():
                            if property_name.lower() in key.lower():
                                prop_value = value
                                break
                        
                        if prop_value is not None and min_val <= prop_value <= max_val:
                            matches.append(fm)
        
        return matches
    
    def find_by_performance_category(self, category: str) -> List[Dict[str, Any]]:
        """Find formulations by performance category."""
        category_lower = category.lower()
        
        if 'performance' in category_lower or 'quality' in category_lower:
            return self.high_performance.copy()
        elif 'cost' in category_lower or 'budget' in category_lower:
            return self.cost_optimized.copy()
        elif 'eco' in category_lower or 'green' in category_lower:
            return self.eco_friendly.copy()
        else:
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            'total_formulations': len(self.formulations),
            'applications': len(self.by_application),
            'cost_ranges': len(self.by_cost_range),
            'materials': len(self.by_material),
            'material_combinations': len(self.by_material_combination),
            'complexity_levels': len(self.by_complexity),
            'high_performance_count': len(self.high_performance),
            'cost_optimized_count': len(self.cost_optimized),
            'eco_friendly_count': len(self.eco_friendly)
        }


class AdvancedSupplierIndex:
    """Advanced supplier indexing with reliability and availability tracking."""
    
    def __init__(self, suppliers: List[Dict[str, Any]]):
        self.suppliers = suppliers
        self._build_advanced_indexes()
    
    def _build_advanced_indexes(self) -> None:
        """Build advanced supplier indexes."""
        logger.info("Building advanced supplier indexes")
        
        with perf_logger.timer("supplier_indexing"):
            self.by_id: Dict[str, Dict[str, Any]] = {}
            self.by_product: Dict[str, List[Dict]] = defaultdict(list)
            self.by_location: Dict[str, List[Dict]] = defaultdict(list)
            self.by_availability: Dict[str, List[Dict]] = defaultdict(list)
            self.by_reliability: Dict[str, List[Dict]] = defaultdict(list)
            self.by_price_range: Dict[str, Dict[Tuple[float, float], List[Dict]]] = defaultdict(lambda: defaultdict(list))
            
            # Performance indexes
            self.reliable_suppliers: List[Dict] = []
            self.fast_delivery: List[Dict] = []
            self.cost_effective: List[Dict] = []
            
            for supplier in self.suppliers:
                self._index_supplier(supplier)
            
            logger.info(f"Built supplier indexes: {len(self.by_product)} products, "
                       f"{len(self.by_location)} locations")
    
    def _index_supplier(self, supplier: Dict[str, Any]) -> None:
        """Index a single supplier."""
        supplier_id = supplier.get('id', '')
        
        # ID index
        if supplier_id:
            self.by_id[supplier_id] = supplier
        
        # Product index
        product = supplier.get('prod', supplier.get('product', ''))
        if product:
            self.by_product[product].append(supplier)
        
        # Location index
        location = supplier.get('loc', supplier.get('location', ''))
        if location:
            self.by_location[location].append(supplier)
        
        # Availability index
        availability = supplier.get('avail', supplier.get('availability', 'Unknown'))
        self.by_availability[availability].append(supplier)
        
        # Reliability index
        reliability = supplier.get('rel_score', supplier.get('reliability_score', 0))
        if reliability >= 4:
            reliability_category = 'high'
        elif reliability >= 3:
            reliability_category = 'medium'
        else:
            reliability_category = 'low'
        
        self.by_reliability[reliability_category].append(supplier)
        
        # Price range index
        if product:
            price = supplier.get('price', 0)
            price_per_kg = price / 1000 if price > 1000 else price
            
            if price_per_kg > 0:
                # Create price buckets
                bucket = (int(price_per_kg // 50) * 50, int(price_per_kg // 50) * 50 + 50)
                self.by_price_range[product][bucket].append(supplier)
        
        # Performance categories
        if reliability >= 4:
            self.reliable_suppliers.append(supplier)
        
        lead_time = supplier.get('lead_d', supplier.get('lead_time_days', 999))
        if lead_time <= 7:
            self.fast_delivery.append(supplier)
        
        if price_per_kg > 0 and price_per_kg < 100:  # Arbitrary threshold
            self.cost_effective.append(supplier)
    
    def find_available_suppliers(self, product: str, min_quantity: int = 0, 
                               max_price: Optional[float] = None) -> List[Dict[str, Any]]:
        """Find available suppliers with advanced filtering."""
        product_suppliers = self.by_product.get(product, [])
        
        available = []
        for supplier in product_suppliers:
            # Check availability
            availability = supplier.get('avail', supplier.get('availability', 'Unknown'))
            if availability not in ['Yes', 'Limited']:
                continue
            
            # Check minimum order quantity
            min_order = supplier.get('min_ord', supplier.get('min_order_kg', 0))
            if min_order > min_quantity:
                continue
            
            # Check price constraint
            if max_price is not None:
                price = supplier.get('price', 0)
                price_per_kg = price / 1000 if price > 1000 else price
                if price_per_kg > max_price:
                    continue
            
            available.append(supplier)
        
        # Sort by reliability, availability, and price
        available.sort(key=lambda s: (
            -s.get('rel_score', s.get('reliability_score', 0)),  # Higher reliability first
            0 if s.get('avail', s.get('availability', '')) == 'Yes' else 1,  # Available first
            s.get('price', s.get('price_per_kg', 999))  # Lower price first
        ))
        
        return available
    
    def find_by_location(self, location: str, radius_km: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find suppliers by location with optional radius."""
        # Simple location matching for now
        location_lower = location.lower()
        matches = []
        
        for loc, suppliers in self.by_location.items():
            if location_lower in loc.lower() or loc.lower() in location_lower:
                matches.extend(suppliers)
        
        return matches
    
    def find_by_reliability(self, min_reliability: float) -> List[Dict[str, Any]]:
        """Find suppliers by minimum reliability score."""
        matches = []
        
        for supplier in self.suppliers:
            reliability = supplier.get('rel_score', supplier.get('reliability_score', 0))
            if reliability >= min_reliability:
                matches.append(supplier)
        
        return matches
    
    def get_price_trends(self, product: str, months: int = 6) -> Dict[str, Any]:
        """Get price trends for a product."""
        product_suppliers = self.by_product.get(product, [])
        
        prices = []
        for supplier in product_suppliers:
            price = supplier.get('price', 0)
            price_per_kg = price / 1000 if price > 1000 else price
            month = supplier.get('month', '')
            
            if price_per_kg > 0 and month:
                prices.append({
                    'month': month,
                    'price': price_per_kg,
                    'supplier': supplier.get('name', 'Unknown')
                })
        
        if not prices:
            return {'product': product, 'trend': 'no_data'}
        
        # Sort by month (simple string sort for now)
        prices.sort(key=lambda x: x['month'])
        
        # Calculate trend
        if len(prices) >= 2:
            first_price = prices[0]['price']
            last_price = prices[-1]['price']
            trend = 'increasing' if last_price > first_price else 'decreasing' if last_price < first_price else 'stable'
        else:
            trend = 'stable'
        
        return {
            'product': product,
            'trend': trend,
            'price_points': prices,
            'current_avg_price': sum(p['price'] for p in prices[-3:]) / min(3, len(prices)),
            'min_price': min(p['price'] for p in prices),
            'max_price': max(p['price'] for p in prices)
        }
    
    def get_supplier_performance_metrics(self, supplier_id: str) -> Dict[str, Any]:
        """Get comprehensive performance metrics for a supplier."""
        supplier = self.by_id.get(supplier_id)
        if not supplier:
            return {'error': 'Supplier not found'}
        
        return {
            'supplier_id': supplier_id,
            'name': supplier.get('name', 'Unknown'),
            'reliability_score': supplier.get('rel_score', supplier.get('reliability_score', 0)),
            'availability': supplier.get('avail', supplier.get('availability', 'Unknown')),
            'lead_time_days': supplier.get('lead_d', supplier.get('lead_time_days', 0)),
            'certifications': supplier.get('cert', supplier.get('certifications', '')),
            'location': supplier.get('loc', supplier.get('location', '')),
            'products_supplied': [supplier.get('prod', supplier.get('product', ''))],
            'performance_category': self._get_supplier_category(supplier)
        }
    
    def _get_supplier_category(self, supplier: Dict[str, Any]) -> str:
        """Categorize supplier performance."""
        reliability = supplier.get('rel_score', supplier.get('reliability_score', 0))
        availability = supplier.get('avail', supplier.get('availability', 'Unknown'))
        lead_time = supplier.get('lead_d', supplier.get('lead_time_days', 999))
        
        if reliability >= 4 and availability == 'Yes' and lead_time <= 7:
            return 'premium'
        elif reliability >= 3 and availability in ['Yes', 'Limited'] and lead_time <= 14:
            return 'standard'
        else:
            return 'basic'


class GraphRAGDatabaseManager:
    """Advanced database manager for GraphRAG system with comprehensive indexing."""
    
    def __init__(self):
        self.loader = AdvancedDataLoader()
        self._data: Optional[Dict[str, Any]] = None
        self._formulation_index: Optional[AdvancedFormulationIndex] = None
        self._supplier_index: Optional[AdvancedSupplierIndex] = None
        self._lock = threading.RLock()
        self._initialization_time: Optional[float] = None
    
    @ExceptionHandler.handle_exceptions
    def initialize(self, force_reload: bool = False) -> None:
        """Initialize database with comprehensive validation and indexing."""
        with self._lock:
            if self._data is not None and not force_reload:
                return
            
            start_time = time.time()
            logger.info("Initializing GraphRAG database manager")
            
            try:
                # Load all data
                self._data = self.loader.load_all_databases(force_reload)
                
                # Build advanced indexes
                self._formulation_index = AdvancedFormulationIndex(self._data['formulations'])
                self._supplier_index = AdvancedSupplierIndex(self._data['suppliers'])
                
                self._initialization_time = time.time() - start_time
                
                logger.info(f"GraphRAG database manager initialized successfully in {self._initialization_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                raise DatabaseError(f"Failed to initialize database: {e}")
    
    @property
    def formulations(self) -> List[Dict[str, Any]]:
        """Get formulations data."""
        if self._data is None:
            self.initialize()
        return self._data['formulations']
    
    @property
    def suppliers(self) -> List[Dict[str, Any]]:
        """Get suppliers data."""
        if self._data is None:
            self.initialize()
        return self._data['suppliers']
    
    @property
    def ingredients(self) -> Dict[str, Any]:
        """Get ingredients data."""
        if self._data is None:
            self.initialize()
        return self._data['ingredients']
    
    @property
    def standards(self) -> Dict[str, Any]:
        """Get compliance standards."""
        if self._data is None:
            self.initialize()
        return self._data['standards']
    
    @property
    def defects(self) -> List[Dict[str, Any]]:
        """Get defects data."""
        if self._data is None:
            self.initialize()
        return self._data.get('defects', [])
    
    @property
    def process_params(self) -> List[Dict[str, Any]]:
        """Get process parameters data."""
        if self._data is None:
            self.initialize()
        return self._data.get('process_params', [])
    
    @property
    def formulation_index(self) -> AdvancedFormulationIndex:
        """Get advanced formulation index."""
        if self._formulation_index is None:
            self.initialize()
        return self._formulation_index
    
    @property
    def supplier_index(self) -> AdvancedSupplierIndex:
        """Get advanced supplier index."""
        if self._supplier_index is None:
            self.initialize()
        return self._supplier_index
    
    def reload_data(self) -> None:
        """Reload data from files (for development/testing)."""
        with self._lock:
            logger.info("Reloading GraphRAG database")
            self._data = None
            self._formulation_index = None
            self._supplier_index = None
            self.initialize(force_reload=True)
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        if self._data is None:
            self.initialize()
        
        stats = {
            'initialization_time': self._initialization_time,
            'data_counts': {
                'formulations': len(self._data.get('formulations', [])),
                'suppliers': len(self._data.get('suppliers', [])),
                'ingredients': len(self._data.get('ingredients', {})),
                'standards': len(self._data.get('standards', {})),
                'defects': len(self._data.get('defects', [])),
                'process_params': len(self._data.get('process_params', []))
            },
            'cache_statistics': self.loader.get_cache_statistics()
        }
        
        if self._formulation_index:
            stats['formulation_index'] = self._formulation_index.get_statistics()
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            health = {
                'status': 'healthy',
                'timestamp': time.time(),
                'checks': {}
            }
            
            # Check data availability
            if self._data is None:
                health['checks']['data_loaded'] = False
                health['status'] = 'unhealthy'
            else:
                health['checks']['data_loaded'] = True
                health['checks']['data_counts'] = {
                    'formulations': len(self._data.get('formulations', [])),
                    'suppliers': len(self._data.get('suppliers', []))
                }
            
            # Check indexes
            health['checks']['formulation_index'] = self._formulation_index is not None
            health['checks']['supplier_index'] = self._supplier_index is not None
            
            # Check file accessibility
            db_files = Config.get_database_files()
            health['checks']['files_accessible'] = all(f.exists() for f in db_files.values())
            
            return health
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }


# Global database manager instance
db_manager = GraphRAGDatabaseManager()