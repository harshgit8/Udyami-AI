#!/usr/bin/env python3
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
import threading
from dataclasses import dataclass

@dataclass
class TableSchema:
    name: str
    columns: List[Tuple[str, str]]  # (column_name, data_type)
    primary_key: str
    indexes: List[str] = None

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.db_path = 'audit_intelligence.db'
            self.logger = self._setup_logger()
            self.schemas = self._define_schemas()
            self.initialized = True
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('DatabaseManager')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _define_schemas(self) -> Dict[str, TableSchema]:
        return {
            'production': TableSchema(
                name='production',
                columns=[
                    ('order_id', 'TEXT PRIMARY KEY'),
                    ('product_type', 'TEXT NOT NULL'),
                    ('quantity', 'INTEGER NOT NULL'),
                    ('due_date', 'DATE NOT NULL'),
                    ('priority', 'TEXT NOT NULL'),
                    ('customer', 'TEXT NOT NULL'),
                    ('notes', 'TEXT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
                ],
                primary_key='order_id',
                indexes=['product_type', 'priority', 'customer', 'due_date']
            ),
            'production_result': TableSchema(
                name='production_result',
                columns=[
                    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('order_id', 'TEXT NOT NULL'),
                    ('decision', 'TEXT NOT NULL'),
                    ('risk_score', 'INTEGER NOT NULL'),
                    ('reason', 'TEXT NOT NULL'),
                    ('machine', 'TEXT'),
                    ('start_time', 'TIMESTAMP'),
                    ('end_time', 'TIMESTAMP'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('FOREIGN KEY (order_id)', 'REFERENCES production(order_id)')
                ],
                primary_key='id',
                indexes=['order_id', 'decision', 'risk_score']
            ),
            'rnd': TableSchema(
                name='rnd',
                columns=[
                    ('request_id', 'TEXT PRIMARY KEY'),
                    ('application', 'TEXT NOT NULL'),
                    ('standards', 'TEXT'),
                    ('cost_target', 'REAL'),
                    ('constraints', 'TEXT'),
                    ('special_notes', 'TEXT'),
                    ('tensile_min', 'INTEGER'),
                    ('chemical_resistance', 'TEXT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
                ],
                primary_key='request_id',
                indexes=['application', 'standards']
            ),
            'rnd_result': TableSchema(
                name='rnd_result',
                columns=[
                    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('request_id', 'TEXT NOT NULL'),
                    ('formulation_id', 'TEXT NOT NULL'),
                    ('base_polymer', 'TEXT'),
                    ('key_additives', 'TEXT'),
                    ('cost_per_kg', 'REAL'),
                    ('ul94_rating', 'TEXT'),
                    ('tensile_mpa', 'INTEGER'),
                    ('loi_percent', 'INTEGER'),
                    ('rohs_compliant', 'TEXT'),
                    ('reach_compliant', 'TEXT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('FOREIGN KEY (request_id)', 'REFERENCES rnd(request_id)')
                ],
                primary_key='id',
                indexes=['request_id', 'formulation_id']
            ),
            'quality': TableSchema(
                name='quality',
                columns=[
                    ('batch_id', 'TEXT PRIMARY KEY'),
                    ('product_type', 'TEXT NOT NULL'),
                    ('quantity', 'INTEGER NOT NULL'),
                    ('inspection_standard', 'TEXT'),
                    ('defects_found', 'TEXT'),
                    ('measurements', 'TEXT'),
                    ('visual_inspection', 'TEXT'),
                    ('special_requirements', 'TEXT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
                ],
                primary_key='batch_id',
                indexes=['product_type', 'inspection_standard']
            ),
            'quality_result': TableSchema(
                name='quality_result',
                columns=[
                    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('batch_id', 'TEXT NOT NULL'),
                    ('inspection_id', 'TEXT NOT NULL'),
                    ('product_type', 'TEXT'),
                    ('quantity', 'INTEGER'),
                    ('total_defects', 'INTEGER'),
                    ('critical_defects', 'INTEGER'),
                    ('major_defects', 'INTEGER'),
                    ('minor_defects', 'INTEGER'),
                    ('defect_rate', 'REAL'),
                    ('severity_level', 'TEXT'),
                    ('pass_fail', 'TEXT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('FOREIGN KEY (batch_id)', 'REFERENCES quality(batch_id)')
                ],
                primary_key='id',
                indexes=['batch_id', 'inspection_id', 'pass_fail']
            ),
            'quotation': TableSchema(
                name='quotation',
                columns=[
                    ('quote_request_id', 'TEXT PRIMARY KEY'),
                    ('customer', 'TEXT NOT NULL'),
                    ('product_type', 'TEXT NOT NULL'),
                    ('quantity', 'INTEGER NOT NULL'),
                    ('application', 'TEXT'),
                    ('quality_standard', 'TEXT'),
                    ('priority', 'TEXT'),
                    ('delivery_required', 'DATE'),
                    ('special_requirements', 'TEXT'),
                    ('material_formulation', 'TEXT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
                ],
                primary_key='quote_request_id',
                indexes=['customer', 'product_type', 'priority']
            ),
            'quotation_result': TableSchema(
                name='quotation_result',
                columns=[
                    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('quote_id', 'TEXT NOT NULL'),
                    ('request_id', 'TEXT NOT NULL'),
                    ('customer', 'TEXT'),
                    ('product', 'TEXT'),
                    ('quantity', 'INTEGER'),
                    ('material_cost', 'REAL'),
                    ('production_cost', 'REAL'),
                    ('quality_cost', 'REAL'),
                    ('risk_premium', 'REAL'),
                    ('subtotal', 'REAL'),
                    ('total_amount', 'REAL'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('FOREIGN KEY (request_id)', 'REFERENCES quotation(quote_request_id)')
                ],
                primary_key='id',
                indexes=['quote_id', 'request_id', 'customer']
            ),
            'invoice': TableSchema(
                name='invoice',
                columns=[
                    ('invoice_request_id', 'TEXT PRIMARY KEY'),
                    ('customer_name', 'TEXT NOT NULL'),
                    ('customer_address', 'TEXT'),
                    ('customer_gstin', 'TEXT'),
                    ('quote_id', 'TEXT'),
                    ('order_id', 'TEXT'),
                    ('po_number', 'TEXT'),
                    ('product_type', 'TEXT'),
                    ('product_description', 'TEXT'),
                    ('quantity_ordered', 'INTEGER'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
                ],
                primary_key='invoice_request_id',
                indexes=['customer_name', 'quote_id', 'order_id']
            ),
            'invoice_result': TableSchema(
                name='invoice_result',
                columns=[
                    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('invoice_number', 'TEXT NOT NULL'),
                    ('invoice_date', 'DATE'),
                    ('due_date', 'DATE'),
                    ('request_id', 'TEXT NOT NULL'),
                    ('customer_name', 'TEXT'),
                    ('customer_gstin', 'TEXT'),
                    ('order_id', 'TEXT'),
                    ('po_number', 'TEXT'),
                    ('product', 'TEXT'),
                    ('quantity', 'INTEGER'),
                    ('total_amount', 'REAL'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('FOREIGN KEY (request_id)', 'REFERENCES invoice(invoice_request_id)')
                ],
                primary_key='id',
                indexes=['invoice_number', 'request_id', 'customer_name']
            ),
            # Cache tables for AI reports
            'production_reports_cache': TableSchema(
                name='production_reports_cache',
                columns=[
                    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('report_hash', 'TEXT UNIQUE NOT NULL'),
                    ('filters_json', 'TEXT NOT NULL'),
                    ('report_content', 'TEXT NOT NULL'),
                    ('ai_insights', 'TEXT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('expires_at', 'TIMESTAMP NOT NULL')
                ],
                primary_key='id',
                indexes=['report_hash', 'created_at']
            ),
            'quality_reports_cache': TableSchema(
                name='quality_reports_cache',
                columns=[
                    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('report_hash', 'TEXT UNIQUE NOT NULL'),
                    ('filters_json', 'TEXT NOT NULL'),
                    ('report_content', 'TEXT NOT NULL'),
                    ('ai_insights', 'TEXT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('expires_at', 'TIMESTAMP NOT NULL')
                ],
                primary_key='id',
                indexes=['report_hash', 'created_at']
            ),
            'quotation_reports_cache': TableSchema(
                name='quotation_reports_cache',
                columns=[
                    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('report_hash', 'TEXT UNIQUE NOT NULL'),
                    ('filters_json', 'TEXT NOT NULL'),
                    ('report_content', 'TEXT NOT NULL'),
                    ('ai_insights', 'TEXT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('expires_at', 'TIMESTAMP NOT NULL')
                ],
                primary_key='id',
                indexes=['report_hash', 'created_at']
            ),
            'invoice_reports_cache': TableSchema(
                name='invoice_reports_cache',
                columns=[
                    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('report_hash', 'TEXT UNIQUE NOT NULL'),
                    ('filters_json', 'TEXT NOT NULL'),
                    ('report_content', 'TEXT NOT NULL'),
                    ('ai_insights', 'TEXT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('expires_at', 'TIMESTAMP NOT NULL')
                ],
                primary_key='id',
                indexes=['report_hash', 'created_at']
            ),
            'rnd_reports_cache': TableSchema(
                name='rnd_reports_cache',
                columns=[
                    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('report_hash', 'TEXT UNIQUE NOT NULL'),
                    ('filters_json', 'TEXT NOT NULL'),
                    ('report_content', 'TEXT NOT NULL'),
                    ('ai_insights', 'TEXT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('expires_at', 'TIMESTAMP NOT NULL')
                ],
                primary_key='id',
                indexes=['report_hash', 'created_at']
            ),
            'schedule_reports_cache': TableSchema(
                name='schedule_reports_cache',
                columns=[
                    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('report_hash', 'TEXT UNIQUE NOT NULL'),
                    ('filters_json', 'TEXT NOT NULL'),
                    ('report_content', 'TEXT NOT NULL'),
                    ('ai_insights', 'TEXT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('expires_at', 'TIMESTAMP NOT NULL')
                ],
                primary_key='id',
                indexes=['report_hash', 'created_at']
            )
        }
    
    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = 10000")
            conn.execute("PRAGMA temp_store = MEMORY")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def initialize_database(self) -> bool:
        try:
            with self.get_connection() as conn:
                for schema in self.schemas.values():
                    # Create table
                    columns_sql = ', '.join([f"{col[0]} {col[1]}" for col in schema.columns])
                    create_sql = f"CREATE TABLE IF NOT EXISTS {schema.name} ({columns_sql})"
                    conn.execute(create_sql)
                    
                    # Create indexes
                    if schema.indexes:
                        for index_col in schema.indexes:
                            index_name = f"idx_{schema.name}_{index_col}"
                            index_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {schema.name}({index_col})"
                            conn.execute(index_sql)
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                return True
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            return False
    
    def insert_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        try:
            with self.get_connection() as conn:
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                sql = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
                conn.execute(sql, list(data.values()))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to insert data into {table_name}: {e}")
            return False
    
    def bulk_insert(self, table_name: str, data_list: List[Dict[str, Any]]) -> bool:
        if not data_list:
            return True
        
        try:
            with self.get_connection() as conn:
                columns = ', '.join(data_list[0].keys())
                placeholders = ', '.join(['?' for _ in data_list[0]])
                sql = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
                
                values_list = [list(data.values()) for data in data_list]
                conn.executemany(sql, values_list)
                conn.commit()
                self.logger.info(f"Bulk inserted {len(data_list)} records into {table_name}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to bulk insert into {table_name}: {e}")
            return False
    
    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            return []
    
    def execute(self, sql: str, params: tuple = ()) -> bool:
        try:
            with self.get_connection() as conn:
                conn.execute(sql, params)
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Execute failed: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        try:
            with self.get_connection() as conn:
                # Get table schema
                schema_info = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                
                # Get row count
                count_result = conn.execute(f"SELECT COUNT(*) as count FROM {table_name}").fetchone()
                
                return {
                    'table_name': table_name,
                    'columns': [dict(col) for col in schema_info],
                    'row_count': count_result['count'] if count_result else 0
                }
        except Exception as e:
            self.logger.error(f"Failed to get table info for {table_name}: {e}")
            return {}
    
    def cleanup_expired_cache(self) -> bool:
        try:
            cache_tables = [name for name in self.schemas.keys() if name.endswith('_cache')]
            with self.get_connection() as conn:
                for table in cache_tables:
                    conn.execute(f"DELETE FROM {table} WHERE expires_at < datetime('now')")
                conn.commit()
                self.logger.info("Cleaned up expired cache entries")
                return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup cache: {e}")
            return False