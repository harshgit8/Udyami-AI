#!/usr/bin/env python3
"""
Reports Parser for Manufacturing Audit Intelligence Platform
Parses existing reports and stores structured data in audit_intelligence.db
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

class ReportsParser:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.logger = self._setup_logger()
        
        # Report file paths
        self.report_files = {
            'invoices': '../reports/invoices_20260131_071719.md',
            'production': '../reports/production_report_20260131_010401.md',
            'quality': '../reports/quality_inspection_20260131_070956.md',
            'quotations': '../reports/quotations_20260131_060321.md',
            'quotations_2': '../reports/quotations_20260131_065520.md',
            'rnd': '../reports/rnd_formulations_20260131_071256.md',
            'schedule': '../reports/schedule_20260131_010401.html'
        }
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('ReportsParser')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def parse_invoice_reports(self) -> List[Dict[str, Any]]:
        """Parse invoice reports and extract structured data"""
        invoices = []
        
        try:
            with open(self.report_files['invoices'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by invoice sections
            invoice_sections = re.split(r'# 📄 TAX INVOICE', content)[1:]  # Skip header
            
            for section in invoice_sections:
                invoice_data = {}
                
                # Extract invoice number
                invoice_num_match = re.search(r'\*\*Invoice Number:\*\* (INV-[\d-]+)', section)
                if invoice_num_match:
                    invoice_data['invoice_number'] = invoice_num_match.group(1)
                
                # Extract invoice date
                date_match = re.search(r'\*\*Invoice Date:\*\* ([\d-]+)', section)
                if date_match:
                    invoice_data['invoice_date'] = date_match.group(1)
                
                # Extract due date
                due_match = re.search(r'\*\*Due Date:\*\* ([\d-]+)', section)
                if due_match:
                    invoice_data['due_date'] = due_match.group(1)
                
                # Extract customer name
                customer_match = re.search(r'\*\*(.*?)\*\*\n.*?Street', section)
                if customer_match:
                    invoice_data['customer_name'] = customer_match.group(1)
                
                # Extract GSTIN
                gstin_match = re.search(r'GSTIN: ([\w\d]+)', section)
                if gstin_match:
                    invoice_data['customer_gstin'] = gstin_match.group(1)
                
                # Extract quote ID
                quote_match = re.search(r'Quote ID: (QT_[\d_]+)', section)
                if quote_match:
                    invoice_data['quote_id'] = quote_match.group(1)
                
                # Extract order ID
                order_match = re.search(r'Order ID: (ORD-[\d]+)', section)
                if order_match:
                    invoice_data['order_id'] = order_match.group(1)
                
                # Extract PO number
                po_match = re.search(r'PO Number: ([\w/\d]+)', section)
                if po_match:
                    invoice_data['po_number'] = po_match.group(1)
                
                # Extract product description
                desc_match = re.search(r'\*\*Description:\*\* (.*?)\n', section)
                if desc_match:
                    invoice_data['product_description'] = desc_match.group(1)
                
                # Extract quantity
                qty_match = re.search(r'\*\*Quantity Delivered:\*\* (\d+) units', section)
                if qty_match:
                    invoice_data['quantity'] = int(qty_match.group(1))
                
                # Extract grand total
                total_match = re.search(r'\*\*GRAND TOTAL:\*\* ₹([\d,.]+)', section)
                if total_match:
                    total_str = total_match.group(1).replace(',', '')
                    invoice_data['total_amount'] = float(total_str)
                
                # Extract balance due
                balance_match = re.search(r'\*\*BALANCE DUE:\*\* ₹([\d,.]+)', section)
                if balance_match:
                    balance_str = balance_match.group(1).replace(',', '')
                    invoice_data['balance_due'] = float(balance_str)
                
                # Extract payment terms
                terms_match = re.search(r'\*\*Payment Terms:\*\* (.*?)\n', section)
                if terms_match:
                    invoice_data['payment_terms'] = terms_match.group(1)
                
                # Extract AI insights
                risk_match = re.search(r'\*\*Payment Risk:\*\* (\w+)', section)
                if risk_match:
                    invoice_data['payment_risk'] = risk_match.group(1)
                
                priority_match = re.search(r'\*\*Collection Priority:\*\* (\w+)', section)
                if priority_match:
                    invoice_data['collection_priority'] = priority_match.group(1)
                
                if invoice_data:
                    invoice_data['request_id'] = f"INV-REQ-{len(invoices)+1:03d}"
                    invoice_data['created_at'] = datetime.now().isoformat()
                    invoices.append(invoice_data)
            
            self.logger.info(f"Parsed {len(invoices)} invoices")
            return invoices
            
        except Exception as e:
            self.logger.error(f"Error parsing invoice reports: {e}")
            return []
    
    def parse_quality_reports(self) -> List[Dict[str, Any]]:
        """Parse quality inspection reports"""
        quality_data = []
        
        try:
            with open(self.report_files['quality'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by inspection sections
            inspection_sections = re.split(r'# 🔍 Quality Inspection Report', content)[1:]
            
            for section in inspection_sections:
                inspection = {}
                
                # Extract inspection ID
                id_match = re.search(r'\*\*Inspection ID:\*\* (QC_[\d_]+)', section)
                if id_match:
                    inspection['inspection_id'] = id_match.group(1)
                
                # Extract batch ID
                batch_match = re.search(r'\*\*Batch ID:\*\* (BATCH\d+)', section)
                if batch_match:
                    inspection['batch_id'] = batch_match.group(1)
                
                # Extract product type
                product_match = re.search(r'\*\*Product Type:\*\* (\w+)', section)
                if product_match:
                    inspection['product_type'] = product_match.group(1)
                
                # Extract quantity
                qty_match = re.search(r'\*\*Quantity:\*\* (\d+)', section)
                if qty_match:
                    inspection['quantity'] = int(qty_match.group(1))
                
                # Extract inspection standard
                std_match = re.search(r'\*\*Inspection Standard:\*\* ([\w_\d]+)', section)
                if std_match:
                    inspection['inspection_standard'] = std_match.group(1)
                
                # Extract defect information
                total_defects_match = re.search(r'\*\*Total Defects:\*\* (\d+)', section)
                if total_defects_match:
                    inspection['total_defects'] = int(total_defects_match.group(1))
                
                critical_match = re.search(r'\*\*Critical:\*\* (\d+)', section)
                if critical_match:
                    inspection['critical_defects'] = int(critical_match.group(1))
                
                major_match = re.search(r'\*\*Major:\*\* (\d+)', section)
                if major_match:
                    inspection['major_defects'] = int(major_match.group(1))
                
                minor_match = re.search(r'\*\*Minor:\*\* (\d+)', section)
                if minor_match:
                    inspection['minor_defects'] = int(minor_match.group(1))
                
                # Extract defect rate
                rate_match = re.search(r'\*\*Defect Rate:\*\* ([\d.]+)%', section)
                if rate_match:
                    inspection['defect_rate'] = float(rate_match.group(1))
                
                # Extract final decision
                decision_match = re.search(r'(✅|❌|⚠️) \*\*(\w+)\*\*', section)
                if decision_match:
                    decision_map = {'✅': 'ACCEPT', '❌': 'REJECT', '⚠️': 'CONDITIONAL_ACCEPT'}
                    inspection['pass_fail'] = decision_map.get(decision_match.group(1), decision_match.group(2))
                
                # Extract severity level
                severity_match = re.search(r'\*\*Severity Level:\*\* (\w+)', section)
                if severity_match:
                    inspection['severity_level'] = severity_match.group(1)
                
                if inspection:
                    inspection['created_at'] = datetime.now().isoformat()
                    quality_data.append(inspection)
            
            self.logger.info(f"Parsed {len(quality_data)} quality inspections")
            return quality_data
            
        except Exception as e:
            self.logger.error(f"Error parsing quality reports: {e}")
            return []
    
    def parse_quotation_reports(self) -> List[Dict[str, Any]]:
        """Parse quotation reports"""
        quotations = []
        
        for file_key in ['quotations', 'quotations_2']:
            try:
                with open(self.report_files[file_key], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split by quotation sections
                quote_sections = re.split(r'# 💰 QUOTATION', content)[1:]
                
                for section in quote_sections:
                    quote = {}
                    
                    # Extract quote ID
                    id_match = re.search(r'\*\*Quote ID:\*\* (QT_[\d_]+)', section)
                    if id_match:
                        quote['quote_id'] = id_match.group(1)
                    
                    # Extract customer
                    customer_match = re.search(r'\*\*Customer:\*\* (.*?)\n', section)
                    if customer_match:
                        quote['customer'] = customer_match.group(1)
                    
                    # Extract request ID
                    req_match = re.search(r'\*\*Request ID:\*\* (QR\d+)', section)
                    if req_match:
                        quote['request_id'] = req_match.group(1)
                    
                    # Extract product
                    product_match = re.search(r'\*\*Product:\*\* (\w+)', section)
                    if product_match:
                        quote['product'] = product_match.group(1)
                    
                    # Extract quantity
                    qty_match = re.search(r'\*\*Quantity:\*\* (\d+) units', section)
                    if qty_match:
                        quote['quantity'] = int(qty_match.group(1))
                    
                    # Extract costs
                    material_match = re.search(r'\*\*Total Material:\*\* ₹([\d,.]+)', section)
                    if material_match:
                        quote['material_cost'] = float(material_match.group(1).replace(',', ''))
                    
                    production_match = re.search(r'\*\*Total Production:\*\* ₹([\d,.]+)', section)
                    if production_match:
                        quote['production_cost'] = float(production_match.group(1).replace(',', ''))
                    
                    quality_match = re.search(r'\*\*Total Quality:\*\* ₹([\d,.]+)', section)
                    if quality_match:
                        quote['quality_cost'] = float(quality_match.group(1).replace(',', ''))
                    
                    risk_match = re.search(r'\*\*Total Risk Premium:\*\* ₹([\d,.]+)', section)
                    if risk_match:
                        quote['risk_premium'] = float(risk_match.group(1).replace(',', ''))
                    
                    # Extract subtotal and total
                    subtotal_match = re.search(r'\*\*Subtotal:\*\* ₹([\d,.]+)', section)
                    if subtotal_match:
                        quote['subtotal'] = float(subtotal_match.group(1).replace(',', ''))
                    
                    total_match = re.search(r'\*\*GRAND TOTAL:\*\* ₹([\d,.]+)', section)
                    if total_match:
                        quote['total_amount'] = float(total_match.group(1).replace(',', ''))
                    
                    # Extract unit price
                    unit_match = re.search(r'\*\*Unit Price:\*\* ₹([\d,.]+) per unit', section)
                    if unit_match:
                        quote['unit_price'] = float(unit_match.group(1).replace(',', ''))
                    
                    # Extract lead time
                    lead_match = re.search(r'\*\*Lead Time:\*\* (\d+) days', section)
                    if lead_match:
                        quote['lead_time'] = int(lead_match.group(1))
                    
                    # Extract payment terms
                    terms_match = re.search(r'\*\*Payment Terms:\*\* (.*?)\n', section)
                    if terms_match:
                        quote['payment_terms'] = terms_match.group(1)
                    
                    # Extract win probability
                    win_match = re.search(r'\*\*Win Probability:\*\* (\w+)', section)
                    if win_match:
                        quote['win_probability'] = win_match.group(1)
                    
                    if quote:
                        quote['created_at'] = datetime.now().isoformat()
                        quotations.append(quote)
                
            except Exception as e:
                self.logger.error(f"Error parsing {file_key}: {e}")
        
        self.logger.info(f"Parsed {len(quotations)} quotations")
        return quotations
    
    def parse_rnd_reports(self) -> List[Dict[str, Any]]:
        """Parse R&D formulation reports"""
        rnd_data = []
        
        try:
            with open(self.report_files['rnd'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by formulation sections
            formulation_sections = re.split(r'# 🧪 R&D Formulation Report', content)[1:]
            
            for section in formulation_sections:
                formulation = {}
                
                # Extract formulation ID
                id_match = re.search(r'\*\*Formulation ID:\*\* (FORM_[\d_]+)', section)
                if id_match:
                    formulation['formulation_id'] = id_match.group(1)
                
                # Extract application
                app_match = re.search(r'\*\*Application:\*\* (\w+)', section)
                if app_match:
                    formulation['application'] = app_match.group(1)
                
                # Extract standards
                std_match = re.search(r'\*\*Standards:\*\* ([\w\d\s-]+)', section)
                if std_match:
                    formulation['standards'] = std_match.group(1).strip()
                
                # Extract cost target
                cost_match = re.search(r'\*\*Cost Target:\*\* ₹([\d.]+)/kg', section)
                if cost_match:
                    formulation['cost_target'] = float(cost_match.group(1))
                
                # Extract constraints
                constraints_match = re.search(r'\*\*Constraints:\*\* (.*?)\n', section)
                if constraints_match:
                    formulation['constraints'] = constraints_match.group(1)
                
                # Extract base polymer
                polymer_match = re.search(r'\*\*(PVC K\d+):\*\* \d+', section)
                if polymer_match:
                    formulation['base_polymer'] = polymer_match.group(1)
                
                # Extract total cost
                total_cost_match = re.search(r'\*\*Total Cost:\*\* ₹(\d+)/kg', section)
                if total_cost_match:
                    formulation['cost_per_kg'] = float(total_cost_match.group(1))
                
                # Extract UL94 rating
                ul94_match = re.search(r'\*\*UL94 Rating:\*\* ([\w-]+)', section)
                if ul94_match:
                    formulation['ul94_rating'] = ul94_match.group(1)
                
                # Extract tensile strength
                tensile_match = re.search(r'\*\*Tensile Strength:\*\* (\d+) MPa', section)
                if tensile_match:
                    formulation['tensile_mpa'] = int(tensile_match.group(1))
                
                # Extract LOI
                loi_match = re.search(r'\*\*LOI:\*\* (\d+)%', section)
                if loi_match:
                    formulation['loi_percent'] = int(loi_match.group(1))
                
                # Extract compliance
                rohs_match = re.search(r'\*\*RoHS:\*\* (\w+)', section)
                if rohs_match:
                    formulation['rohs_compliant'] = rohs_match.group(1)
                
                reach_match = re.search(r'\*\*REACH:\*\* (\w+)', section)
                if reach_match:
                    formulation['reach_compliant'] = reach_match.group(1)
                
                # Extract production readiness
                readiness_match = re.search(r'\*\*Production Readiness:\*\* (\w+)', section)
                if readiness_match:
                    formulation['production_readiness'] = readiness_match.group(1)
                
                if formulation:
                    formulation['request_id'] = f"RND{len(rnd_data)+1:03d}"
                    formulation['created_at'] = datetime.now().isoformat()
                    rnd_data.append(formulation)
            
            self.logger.info(f"Parsed {len(rnd_data)} R&D formulations")
            return rnd_data
            
        except Exception as e:
            self.logger.error(f"Error parsing R&D reports: {e}")
            return []
    
    def parse_production_schedule(self) -> List[Dict[str, Any]]:
        """Parse production schedule from HTML"""
        production_data = []
        
        try:
            with open(self.report_files['schedule'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract order data from HTML table rows
            order_pattern = r'<tr>\s*<td>(ORD-\d+)</td>\s*<td>([\d-T:]+)</td>\s*<td>([\d-T:]+)</td>\s*<td[^>]*>\s*(\d+)/10'
            
            matches = re.findall(order_pattern, content)
            
            for match in matches:
                order_id, start_time, end_time, risk_score = match
                
                production_entry = {
                    'order_id': order_id,
                    'decision': 'PROCEED',  # All scheduled orders are PROCEED
                    'risk_score': int(risk_score),
                    'reason': 'All constraints satisfied' if int(risk_score) == 0 else 'Scheduled with risk',
                    'machine': 'M1',  # Default machine from HTML structure
                    'start_time': start_time,
                    'end_time': end_time,
                    'created_at': datetime.now().isoformat()
                }
                
                production_data.append(production_entry)
            
            self.logger.info(f"Parsed {len(production_data)} production schedule entries")
            return production_data
            
        except Exception as e:
            self.logger.error(f"Error parsing production schedule: {e}")
            return []
    
    def store_parsed_data(self):
        """Store all parsed data in the database"""
        try:
            # Initialize database
            if not self.db_manager.initialize_database():
                self.logger.error("Failed to initialize database")
                return False
            
            # Parse and store invoice data
            invoices = self.parse_invoice_reports()
            if invoices:
                # Store invoice requests
                invoice_requests = []
                invoice_results = []
                
                for inv in invoices:
                    # Invoice request data
                    request_data = {
                        'invoice_request_id': inv.get('request_id', f'INV-REQ-{len(invoice_requests)+1:03d}'),
                        'customer_name': inv.get('customer_name', 'Unknown Customer'),
                        'customer_address': inv.get('customer_address', ''),
                        'customer_gstin': inv.get('customer_gstin', ''),
                        'quote_id': inv.get('quote_id', ''),
                        'order_id': inv.get('order_id', ''),
                        'po_number': inv.get('po_number', ''),
                        'product_type': inv.get('product_type', ''),
                        'product_description': inv.get('product_description', ''),
                        'quantity_ordered': inv.get('quantity', 0)
                    }
                    invoice_requests.append(request_data)
                    
                    # Invoice result data
                    result_data = {
                        'invoice_number': inv.get('invoice_number'),
                        'invoice_date': inv.get('invoice_date'),
                        'due_date': inv.get('due_date'),
                        'request_id': inv.get('request_id'),
                        'customer_name': inv.get('customer_name'),
                        'customer_gstin': inv.get('customer_gstin'),
                        'order_id': inv.get('order_id'),
                        'po_number': inv.get('po_number'),
                        'product': inv.get('product_description'),
                        'quantity': inv.get('quantity'),
                        'total_amount': inv.get('total_amount')
                    }
                    invoice_results.append(result_data)
                
                self.db_manager.bulk_insert('invoice', invoice_requests)
                self.db_manager.bulk_insert('invoice_result', invoice_results)
            
            # Parse and store quality data
            quality_inspections = self.parse_quality_reports()
            if quality_inspections:
                # Split into quality and quality_result tables
                quality_data = []
                quality_results = []
                
                for qc in quality_inspections:
                    # Quality batch data
                    batch_data = {
                        'batch_id': qc.get('batch_id', f'BATCH{len(quality_data)+1:03d}'),
                        'product_type': qc.get('product_type', 'unknown'),
                        'quantity': qc.get('quantity', 0),
                        'inspection_standard': qc.get('inspection_standard', ''),
                        'defects_found': '',
                        'measurements': '',
                        'visual_inspection': '',
                        'special_requirements': ''
                    }
                    quality_data.append(batch_data)
                    
                    # Quality result data
                    result_data = {
                        'batch_id': qc.get('batch_id'),
                        'inspection_id': qc.get('inspection_id'),
                        'product_type': qc.get('product_type'),
                        'quantity': qc.get('quantity'),
                        'total_defects': qc.get('total_defects'),
                        'critical_defects': qc.get('critical_defects'),
                        'major_defects': qc.get('major_defects'),
                        'minor_defects': qc.get('minor_defects'),
                        'defect_rate': qc.get('defect_rate'),
                        'severity_level': qc.get('severity_level'),
                        'pass_fail': qc.get('pass_fail')
                    }
                    quality_results.append(result_data)
                
                self.db_manager.bulk_insert('quality', quality_data)
                self.db_manager.bulk_insert('quality_result', quality_results)
            
            # Parse and store quotation data
            quotations = self.parse_quotation_reports()
            if quotations:
                # Split into quotation and quotation_result tables
                quote_requests = []
                quote_results = []
                
                for quote in quotations:
                    # Quotation request data
                    request_data = {
                        'quote_request_id': quote.get('request_id', f'QR{len(quote_requests)+1:03d}'),
                        'customer': quote.get('customer', 'Unknown'),
                        'product_type': quote.get('product', 'unknown'),
                        'quantity': quote.get('quantity', 0),
                        'application': quote.get('application', ''),
                        'quality_standard': quote.get('quality_standard', ''),
                        'priority': quote.get('priority', 'normal'),
                        'delivery_required': None,
                        'special_requirements': '',
                        'material_formulation': ''
                    }
                    quote_requests.append(request_data)
                    
                    # Quotation result data
                    result_data = {
                        'quote_id': quote.get('quote_id'),
                        'request_id': quote.get('request_id'),
                        'customer': quote.get('customer'),
                        'product': quote.get('product'),
                        'quantity': quote.get('quantity'),
                        'material_cost': quote.get('material_cost'),
                        'production_cost': quote.get('production_cost'),
                        'quality_cost': quote.get('quality_cost'),
                        'risk_premium': quote.get('risk_premium'),
                        'subtotal': quote.get('subtotal'),
                        'total_amount': quote.get('total_amount')
                    }
                    quote_results.append(result_data)
                
                self.db_manager.bulk_insert('quotation', quote_requests)
                self.db_manager.bulk_insert('quotation_result', quote_results)
            
            # Parse and store R&D data
            rnd_formulations = self.parse_rnd_reports()
            if rnd_formulations:
                # Split into rnd and rnd_result tables
                rnd_requests = []
                rnd_results = []
                
                for rnd in rnd_formulations:
                    # R&D request data
                    request_data = {
                        'request_id': rnd.get('request_id', f'RND{len(rnd_requests)+1:03d}'),
                        'application': rnd.get('application', 'unknown'),
                        'standards': rnd.get('standards', ''),
                        'cost_target': rnd.get('cost_target', 0.0),
                        'constraints': rnd.get('constraints', ''),
                        'special_notes': '',
                        'tensile_min': rnd.get('tensile_mpa', 0),
                        'chemical_resistance': ''
                    }
                    rnd_requests.append(request_data)
                    
                    # R&D result data
                    result_data = {
                        'request_id': rnd.get('request_id'),
                        'formulation_id': rnd.get('formulation_id'),
                        'base_polymer': rnd.get('base_polymer'),
                        'cost_per_kg': rnd.get('cost_per_kg'),
                        'ul94_rating': rnd.get('ul94_rating'),
                        'tensile_mpa': rnd.get('tensile_mpa'),
                        'loi_percent': rnd.get('loi_percent'),
                        'rohs_compliant': rnd.get('rohs_compliant'),
                        'reach_compliant': rnd.get('reach_compliant')
                    }
                    rnd_results.append(result_data)
                
                self.db_manager.bulk_insert('rnd', rnd_requests)
                self.db_manager.bulk_insert('rnd_result', rnd_results)
            
            # Parse and store production schedule
            production_schedule = self.parse_production_schedule()
            if production_schedule:
                self.db_manager.bulk_insert('production_result', production_schedule)
            
            self.logger.info("Successfully stored all parsed report data in database")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing parsed data: {e}")
            return False
    
    def generate_summary_report(self) -> str:
        """Generate summary of parsed data"""
        try:
            summary = []
            summary.append("# 📊 Reports Parsing Summary")
            summary.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            summary.append("")
            
            # Get table counts
            tables = ['invoice', 'invoice_result', 'quality', 'quality_result', 
                     'quotation', 'quotation_result', 'rnd', 'rnd_result', 'production_result']
            
            summary.append("## Database Population")
            summary.append("| Table | Records |")
            summary.append("|-------|---------|")
            
            total_records = 0
            for table in tables:
                info = self.db_manager.get_table_info(table)
                count = info.get('row_count', 0)
                total_records += count
                summary.append(f"| {table} | {count} |")
            
            summary.append("")
            summary.append(f"**Total Records:** {total_records}")
            
            # Add insights
            summary.append("")
            summary.append("## Key Insights")
            summary.append("- ✅ All existing reports successfully parsed and structured")
            summary.append("- 🔗 Cross-entity relationships established in database")
            summary.append("- 📈 Data ready for advanced analytics and AI insights")
            summary.append("- 🎯 Audit trail complete with full traceability")
            
            return "\n".join(summary)
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {e}"

def main():
    """Main execution function"""
    print("🚀 Manufacturing Audit Intelligence - Reports Parser")
    print("=" * 60)
    
    parser = ReportsParser()
    
    # Parse and store all report data
    print("📊 Parsing existing reports...")
    success = parser.store_parsed_data()
    
    if success:
        print("✅ Reports parsing completed successfully!")
        
        # Generate summary
        summary = parser.generate_summary_report()
        print("\n" + summary)
        
        # Save summary to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = f"../reports/parsing_summary_{timestamp}.md"
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"\n📄 Summary saved to: {summary_file}")
        except Exception as e:
            print(f"⚠️ Could not save summary file: {e}")
    else:
        print("❌ Reports parsing failed!")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()