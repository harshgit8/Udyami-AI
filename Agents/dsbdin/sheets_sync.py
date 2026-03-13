#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sheets_client import SheetsClient
from database_manager import DatabaseManager
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import json
import time

class SheetsSyncManager:
    def __init__(self):
        self.sheets_client = SheetsClient()
        self.db_manager = DatabaseManager()
        self.logger = self._setup_logger()
        self.sheet_id = "1QuYN01Rhgua_Em8SE5CIXOzFa8kULWnxFE2_ZOc_P74"
        
        # Sheet name to table mapping
        self.sheet_mappings = {
            'Production': 'production',
            'ProductionResult': 'production_result',
            'RnD': 'rnd',
            'RnDResult': 'rnd_result',
            'Quality': 'quality',
            'QualityResult': 'quality_result',
            'Quotation': 'quotation',
            'QuotationResult': 'quotation_result',
            'Invoice': 'invoice',
            'InvoiceResult': 'invoice_result'
        }
        
        # Column mappings for data transformation
        self.column_mappings = {
            'production': {
                'Order ID': 'order_id',
                'Product Type': 'product_type',
                'Quantity': 'quantity',
                'Due Date': 'due_date',
                'Priority': 'priority',
                'Customer': 'customer',
                'Notes': 'notes'
            },
            'production_result': {
                'Order ID': 'order_id',
                'Decision': 'decision',
                'Risk Score': 'risk_score',
                'Reason': 'reason',
                'Machine': 'machine',
                'Start Time': 'start_time',
                'End Time': 'end_time'
            },
            'rnd': {
                'Request ID': 'request_id',
                'Application': 'application',
                'Standards': 'standards',
                'Cost Target (₹/kg)': 'cost_target',
                'Constraints': 'constraints',
                'Special Notes': 'special_notes',
                'Tensile Min (MPa)': 'tensile_min',
                'Chemical Resistance': 'chemical_resistance'
            },
            'rnd_result': {
                'Request ID': 'request_id',
                'Formulation ID': 'formulation_id',
                'Base Polymer': 'base_polymer',
                'Key Additives': 'key_additives',
                'Cost (₹/kg)': 'cost_per_kg',
                'UL94 Rating': 'ul94_rating',
                'Tensile (MPa)': 'tensile_mpa',
                'LOI (%)': 'loi_percent',
                'RoHS': 'rohs_compliant',
                'REACH': 'reach_compliant'
            },
            'quality': {
                'Batch ID': 'batch_id',
                'Product Type': 'product_type',
                'Quantity': 'quantity',
                'Inspection Standard': 'inspection_standard',
                'Defects Found': 'defects_found',
                'Measurements': 'measurements',
                'Visual Inspection': 'visual_inspection',
                'Special Requirements': 'special_requirements'
            },
            'quality_result': {
                'Batch ID': 'batch_id',
                'Inspection ID': 'inspection_id',
                'Product Type': 'product_type',
                'Quantity': 'quantity',
                'Total Defects': 'total_defects',
                'Critical': 'critical_defects',
                'Major': 'major_defects',
                'Minor': 'minor_defects',
                'Defect Rate %': 'defect_rate',
                'Severity Level': 'severity_level',
                'Pass/Fail': 'pass_fail'
            },
            'quotation': {
                'Quote Request ID': 'quote_request_id',
                'Customer': 'customer',
                'Product Type': 'product_type',
                'Quantity': 'quantity',
                'Application': 'application',
                'Quality Standard': 'quality_standard',
                'Priority': 'priority',
                'Delivery Required': 'delivery_required',
                'Special Requirements': 'special_requirements',
                'Material Formulation': 'material_formulation'
            },
            'quotation_result': {
                'Quote ID': 'quote_id',
                'Request ID': 'request_id',
                'Customer': 'customer',
                'Product': 'product',
                'Quantity': 'quantity',
                'Material Cost (₹)': 'material_cost',
                'Production Cost (₹)': 'production_cost',
                'Quality Cost (₹)': 'quality_cost',
                'Risk Premium (₹)': 'risk_premium',
                'Subtotal (₹)': 'subtotal',
                'Total Amount (₹)': 'total_amount'
            },
            'invoice': {
                'Invoice Request ID': 'invoice_request_id',
                'Customer Name': 'customer_name',
                'Customer Address': 'customer_address',
                'Customer GSTIN': 'customer_gstin',
                'Quote ID': 'quote_id',
                'Order ID': 'order_id',
                'PO Number': 'po_number',
                'Product Type': 'product_type',
                'Product Description': 'product_description',
                'Quantity Ordered': 'quantity_ordered'
            },
            'invoice_result': {
                'Invoice Number': 'invoice_number',
                'Invoice Date': 'invoice_date',
                'Due Date': 'due_date',
                'Request ID': 'request_id',
                'Customer Name': 'customer_name',
                'Customer GSTIN': 'customer_gstin',
                'Order ID': 'order_id',
                'PO Number': 'po_number',
                'Product': 'product',
                'Quantity': 'quantity',
                'Total Amount (₹)': 'total_amount'
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('SheetsSyncManager')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _clean_value(self, value: str) -> Any:
        """Clean and convert values from sheets"""
        if not value or value.strip() == '':
            return None
        
        value = value.strip()
        
        # Try to convert to number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Handle date formats
        if len(value) == 10 and value.count('-') == 2:
            try:
                datetime.strptime(value, '%Y-%m-%d')
                return value
            except ValueError:
                pass
        
        return value
    
    def _transform_row(self, headers: List[str], row: List[str], table_name: str) -> Dict[str, Any]:
        """Transform a row from sheets format to database format"""
        if table_name not in self.column_mappings:
            return {}
        
        mapping = self.column_mappings[table_name]
        transformed = {}
        
        for i, header in enumerate(headers):
            if header in mapping and i < len(row):
                db_column = mapping[header]
                value = self._clean_value(row[i])
                if value is not None:
                    transformed[db_column] = value
        
        return transformed
    
    def sync_sheet_to_table(self, sheet_name: str, table_name: str) -> bool:
        """Sync a single sheet to database table"""
        try:
            self.logger.info(f"Syncing {sheet_name} to {table_name}")
            
            # Get data from sheet
            range_name = f"{sheet_name}!A1:Z10000"
            result = self.sheets_client.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id, range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                self.logger.warning(f"No data found in {sheet_name}")
                return True
            
            headers = values[0]
            data_rows = values[1:]
            
            # Transform data
            transformed_data = []
            for row in data_rows:
                if any(cell.strip() for cell in row if cell):  # Skip empty rows
                    transformed_row = self._transform_row(headers, row, table_name)
                    if transformed_row:
                        transformed_data.append(transformed_row)
            
            # Bulk insert to database
            if transformed_data:
                success = self.db_manager.bulk_insert(table_name, transformed_data)
                if success:
                    self.logger.info(f"Successfully synced {len(transformed_data)} records to {table_name}")
                    return True
                else:
                    self.logger.error(f"Failed to sync data to {table_name}")
                    return False
            else:
                self.logger.warning(f"No valid data to sync for {table_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error syncing {sheet_name} to {table_name}: {e}")
            return False
    
    def sync_all_sheets(self) -> Dict[str, bool]:
        """Sync all sheets to database"""
        results = {}
        
        # Initialize database first
        if not self.db_manager.initialize_database():
            self.logger.error("Failed to initialize database")
            return results
        
        # Sync each sheet
        for sheet_name, table_name in self.sheet_mappings.items():
            results[sheet_name] = self.sync_sheet_to_table(sheet_name, table_name)
            time.sleep(0.5)  # Rate limiting
        
        # Cleanup expired cache
        self.db_manager.cleanup_expired_cache()
        
        return results
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        status = {
            'last_sync': datetime.now().isoformat(),
            'tables': {}
        }
        
        for table_name in self.sheet_mappings.values():
            table_info = self.db_manager.get_table_info(table_name)
            status['tables'][table_name] = {
                'row_count': table_info.get('row_count', 0),
                'columns': len(table_info.get('columns', []))
            }
        
        return status
    
    def force_refresh(self) -> bool:
        """Force refresh all data"""
        try:
            # Clear existing data
            for table_name in self.sheet_mappings.values():
                self.db_manager.execute(f"DELETE FROM {table_name}")
            
            # Re-sync all data
            results = self.sync_all_sheets()
            
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            self.logger.info(f"Force refresh completed: {success_count}/{total_count} sheets synced successfully")
            return success_count == total_count
            
        except Exception as e:
            self.logger.error(f"Force refresh failed: {e}")
            return False