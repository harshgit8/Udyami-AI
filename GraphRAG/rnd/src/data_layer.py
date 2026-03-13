"""Production data layer for RND Agent."""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
import threading
from .config import Config
from .exceptions import DatabaseError, DataValidationError
from .validators import DataValidator, FORMULATION_SCHEMA, SUPPLIER_SCHEMA, INGREDIENT_SCHEMA
from .logging_config import get_logger

logger = get_logger(__name__)


class DataLoader:
    """Thread-safe production data loader with caching and validation."""
    
    _instance: Optional['DataLoader'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'DataLoader':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self.db_files = Config.get_database_files()
        self._cache: Dict[str, Any] = {}
        self._cache_file = Path('data_cache.pkl')
        self._initialized = True
        logger.info("DataLoader initialized")
    
    def load_all_databases(self) -> Dict[str, Any]:
        """Load and validate all databases with caching."""
        try:
            # Try loading from cache first
            if self._cache_file.exists():
                try:
                    with open(self._cache_file, 'rb') as f:
                        cached_data = pickle.load(f)
                    
                    # Validate cache is still fresh
                    if self._is_cache_fresh(cached_data):
                        logger.info("Loaded databases from cache")
                        return cached_data['data']
                except Exception as e:
                    logger.warning(f"Cache load failed: {e}, loading from files")
            
            # Load from files
            data = self._load_from_files()
            
            # Cache the data
            self._save_cache(data)
            
            return data
            
        except Exception as e:
            raise DatabaseError(f"Failed to load databases: {e}")
    
    def _load_from_files(self) -> Dict[str, Any]:
        """Load all database files with validation."""
        logger.info("Loading databases from files")
        
        try:
            # Validate against schema
            DataValidator.validate_all_databases(self.db_files)
        except Exception as e:
            logger.warning(f"Database validation issues: {e}")
            # Continue loading despite validation warnings
        
        data = {}
        
        # Load formulations
        data['formulations'] = self._load_json_file('formulations')
        logger.info(f"Loaded {len(data['formulations'])} formulations")
        
        # Load suppliers
        data['suppliers'] = self._load_json_file('suppliers')
        logger.info(f"Loaded {len(data['suppliers'])} suppliers")
        
        # Load ingredients
        data['ingredients'] = self._load_json_file('ingredients')
        logger.info(f"Loaded ingredients database")
        
        # Load standards
        data['standards'] = self._load_json_file('standards')
        logger.info(f"Loaded compliance standards")
        
        # Load defects
        data['defects'] = self._load_json_file('defects')
        logger.info(f"Loaded defect solutions")
        
        # Load process parameters
        data['process_params'] = self._load_json_file('process_params')
        logger.info(f"Loaded process parameters")
        
        # Check data consistency
        issues = DataValidator.check_data_consistency(
            data['formulations'], 
            data['suppliers'], 
            data['ingredients']
        )
        
        if issues:
            logger.warning(f"Data consistency issues: {issues}")
        
        return data
    
    def _load_json_file(self, db_name: str) -> Any:
        """Load and parse JSON file with error handling."""
        file_path = self.db_files[db_name]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.debug(f"Loaded {db_name} from {file_path}")
            return data
            
        except FileNotFoundError:
            raise DatabaseError(f"Database file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise DatabaseError(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            raise DatabaseError(f"Failed to load {file_path}: {e}")
    
    def _is_cache_fresh(self, cached_data: Dict[str, Any]) -> bool:
        """Check if cached data is still fresh."""
        try:
            cache_time = cached_data.get('timestamp', 0)
            
            # Check if any database file is newer than cache
            for file_path in self.db_files.values():
                if file_path.stat().st_mtime > cache_time:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _save_cache(self, data: Dict[str, Any]) -> None:
        """Save data to cache file."""
        try:
            import time
            cache_data = {
                'timestamp': time.time(),
                'data': data
            }
            
            with open(self._cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.debug("Saved data to cache")
            
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")


class FormulationIndex:
    """High-performance indexing for formulation search."""
    
    def __init__(self, formulations: List[Dict[str, Any]]):
        self.formulations = formulations
        self._build_indexes()
    
    def _build_indexes(self) -> None:
        """Build search indexes for fast lookup."""
        logger.info("Building formulation indexes")
        
        self.by_application: Dict[str, List[Dict]] = {}
        self.by_cost_range: Dict[Tuple[int, int], List[Dict]] = {}
        self.by_material: Dict[str, List[Dict]] = {}
        
        for fm in self.formulations:
            # Application index
            app = fm.get('app', fm.get('application', '')).lower()
            if app:
                if app not in self.by_application:
                    self.by_application[app] = []
                self.by_application[app].append(fm)
            
            # Cost range index (₹10 buckets)
            cost = fm.get('cost_per_kg', 0)
            if cost > 0:
                bucket = (int(cost // 10) * 10, int(cost // 10) * 10 + 10)
                if bucket not in self.by_cost_range:
                    self.by_cost_range[bucket] = []
                self.by_cost_range[bucket].append(fm)
            
            # Material index
            formulation = fm.get('formula', fm.get('formulation', {}))
            if isinstance(formulation, dict):
                for material in formulation.keys():
                    if material not in self.by_material:
                        self.by_material[material] = []
                    self.by_material[material].append(fm)
        
        logger.info(f"Built indexes: {len(self.by_application)} applications, "
                   f"{len(self.by_cost_range)} cost ranges, "
                   f"{len(self.by_material)} materials")
    
    @lru_cache(maxsize=1000)
    def find_by_application(self, application: str) -> List[Dict[str, Any]]:
        """Find formulations by application (cached)."""
        app_lower = application.lower()
        
        # Exact match first
        if app_lower in self.by_application:
            return self.by_application[app_lower]
        
        # Partial match
        matches = []
        for app, formulations in self.by_application.items():
            if any(word in app for word in app_lower.split()):
                matches.extend(formulations)
        
        return matches
    
    @lru_cache(maxsize=500)
    def find_by_cost_range(self, min_cost: float, max_cost: float) -> List[Dict[str, Any]]:
        """Find formulations within cost range (cached)."""
        matches = []
        
        for (bucket_min, bucket_max), formulations in self.by_cost_range.items():
            if bucket_max >= min_cost and bucket_min <= max_cost:
                for fm in formulations:
                    cost = fm.get('cost_per_kg', 0)
                    if min_cost <= cost <= max_cost:
                        matches.append(fm)
        
        return matches
    
    def find_by_material(self, material: str) -> List[Dict[str, Any]]:
        """Find formulations containing specific material."""
        return self.by_material.get(material, [])


class SupplierIndex:
    """High-performance supplier indexing and search."""
    
    def __init__(self, suppliers: List[Dict[str, Any]]):
        self.suppliers = suppliers
        self._build_indexes()
    
    def _build_indexes(self) -> None:
        """Build supplier search indexes."""
        logger.info("Building supplier indexes")
        
        self.by_product: Dict[str, List[Dict]] = {}
        self.by_location: Dict[str, List[Dict]] = {}
        self.by_availability: Dict[str, List[Dict]] = {}
        
        for supplier in self.suppliers:
            # Product index
            product = supplier.get('product', supplier.get('prod', ''))
            if product:
                if product not in self.by_product:
                    self.by_product[product] = []
                self.by_product[product].append(supplier)
            
            # Location index
            location = supplier.get('location', supplier.get('loc', ''))
            if location:
                if location not in self.by_location:
                    self.by_location[location] = []
                self.by_location[location].append(supplier)
            
            # Availability index
            availability = supplier.get('availability', supplier.get('avail', 'Unknown'))
            if availability not in self.by_availability:
                self.by_availability[availability] = []
            self.by_availability[availability].append(supplier)
        
        logger.info(f"Built supplier indexes: {len(self.by_product)} products, "
                   f"{len(self.by_location)} locations")
    
    def find_available_suppliers(self, product: str, min_quantity: int = 0) -> List[Dict[str, Any]]:
        """Find available suppliers for product with minimum quantity."""
        product_suppliers = self.by_product.get(product, [])
        
        available = []
        for supplier in product_suppliers:
            availability = supplier.get('availability', supplier.get('avail', 'Unknown'))
            min_order = supplier.get('min_order_kg', supplier.get('min_ord', 0))
            
            if availability == 'Yes' and min_order <= min_quantity:
                available.append(supplier)
        
        # Sort by price and reliability
        available.sort(key=lambda s: (
            s.get('price_per_kg', s.get('price', 999) / 1000),
            -s.get('reliability_score', s.get('rel_score', 0))
        ))
        
        return available
    
    def get_price_history(self, product: str) -> List[Tuple[str, float]]:
        """Get price history for product."""
        product_suppliers = self.by_product.get(product, [])
        
        price_history = []
        for supplier in product_suppliers:
            month = supplier.get('month', '')
            price = supplier.get('price_per_kg', supplier.get('price', 0))
            if isinstance(price, (int, float)) and price > 1000:
                price = price / 1000  # Convert from ₹/ton to ₹/kg
            if month and price > 0:
                price_history.append((month, price))
        
        # Sort by month
        price_history.sort(key=lambda x: x[0])
        return price_history


class DatabaseManager:
    """Production database manager with thread-safe operations."""
    
    def __init__(self):
        self.loader = DataLoader()
        self._data: Optional[Dict[str, Any]] = None
        self._formulation_index: Optional[FormulationIndex] = None
        self._supplier_index: Optional[SupplierIndex] = None
        self._lock = threading.RLock()
    
    def initialize(self) -> None:
        """Initialize database with validation and indexing."""
        with self._lock:
            if self._data is not None:
                return
            
            logger.info("Initializing database manager")
            
            # Load all data
            self._data = self.loader.load_all_databases()
            
            # Build indexes
            self._formulation_index = FormulationIndex(self._data['formulations'])
            self._supplier_index = SupplierIndex(self._data['suppliers'])
            
            logger.info("Database manager initialized successfully")
    
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
    def formulation_index(self) -> FormulationIndex:
        """Get formulation index."""
        if self._formulation_index is None:
            self.initialize()
        return self._formulation_index
    
    @property
    def supplier_index(self) -> SupplierIndex:
        """Get supplier index."""
        if self._supplier_index is None:
            self.initialize()
        return self._supplier_index
    
    def reload_data(self) -> None:
        """Reload data from files (for development/testing)."""
        with self._lock:
            logger.info("Reloading database")
            self._data = None
            self._formulation_index = None
            self._supplier_index = None
            self.initialize()


# Global database manager instance
db_manager = DatabaseManager()