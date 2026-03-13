#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import statistics
from collections import defaultdict, Counter

class AIAnalyzer:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.logger = self._setup_logger()
        
        # Analysis templates
        self.analysis_templates = {
            'production': self._analyze_production,
            'quality': self._analyze_quality,
            'quotation': self._analyze_quotation,
            'invoice': self._analyze_invoice,
            'rnd': self._analyze_rnd,
            'cross_analysis': self._cross_analysis
        }
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('AIAnalyzer')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _generate_cache_key(self, analysis_type: str, filters: Dict[str, Any]) -> str:
        """Generate unique cache key for analysis"""
        filter_str = json.dumps(filters, sort_keys=True)
        return hashlib.md5(f"{analysis_type}_{filter_str}".encode()).hexdigest()
    
    def _get_cached_analysis(self, cache_table: str, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis if available and not expired"""
        try:
            query = f"""
            SELECT report_content, ai_insights, created_at 
            FROM {cache_table} 
            WHERE report_hash = ? AND expires_at > datetime('now')
            ORDER BY created_at DESC LIMIT 1
            """
            results = self.db_manager.query(query, (cache_key,))
            
            if results:
                return {
                    'content': results[0]['report_content'],
                    'insights': json.loads(results[0]['ai_insights']) if results[0]['ai_insights'] else {},
                    'cached': True,
                    'created_at': results[0]['created_at']
                }
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached analysis: {e}")
            return None
    
    def _cache_analysis(self, cache_table: str, cache_key: str, filters: Dict[str, Any], 
                       content: str, insights: Dict[str, Any], ttl_hours: int = 24) -> bool:
        """Cache analysis results"""
        try:
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
            
            data = {
                'report_hash': cache_key,
                'filters_json': json.dumps(filters),
                'report_content': content,
                'ai_insights': json.dumps(insights),
                'expires_at': expires_at.isoformat()
            }
            
            return self.db_manager.insert_data(cache_table, data)
        except Exception as e:
            self.logger.error(f"Error caching analysis: {e}")
            return False
    
    def _analyze_production(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze production data"""
        try:
            # Base queries
            base_query = """
            SELECT p.*, pr.decision, pr.risk_score, pr.reason, pr.machine
            FROM production p
            LEFT JOIN production_result pr ON p.order_id = pr.order_id
            """
            
            where_conditions = []
            params = []
            
            if filters:
                if filters.get('priority'):
                    where_conditions.append("p.priority = ?")
                    params.append(filters['priority'])
                if filters.get('customer'):
                    where_conditions.append("p.customer LIKE ?")
                    params.append(f"%{filters['customer']}%")
                if filters.get('date_from'):
                    where_conditions.append("p.due_date >= ?")
                    params.append(filters['date_from'])
                if filters.get('date_to'):
                    where_conditions.append("p.due_date <= ?")
                    params.append(filters['date_to'])
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            data = self.db_manager.query(base_query, tuple(params))
            
            if not data:
                return {'error': 'No production data found'}
            
            # Analysis
            total_orders = len(data)
            priority_dist = Counter(row['priority'] for row in data if row['priority'])
            customer_dist = Counter(row['customer'] for row in data if row['customer'])
            product_dist = Counter(row['product_type'] for row in data if row['product_type'])
            
            # Risk analysis
            risk_scores = [row['risk_score'] for row in data if row['risk_score'] is not None]
            avg_risk = statistics.mean(risk_scores) if risk_scores else 0
            high_risk_orders = len([r for r in risk_scores if r > 5])
            
            # Decision analysis
            decisions = [row['decision'] for row in data if row['decision']]
            decision_dist = Counter(decisions)
            
            # Quantity analysis
            quantities = [row['quantity'] for row in data if row['quantity']]
            total_quantity = sum(quantities)
            avg_quantity = statistics.mean(quantities) if quantities else 0
            
            insights = {
                'total_orders': total_orders,
                'total_quantity': total_quantity,
                'average_quantity': round(avg_quantity, 2),
                'average_risk_score': round(avg_risk, 2),
                'high_risk_orders': high_risk_orders,
                'priority_distribution': dict(priority_dist),
                'customer_distribution': dict(customer_dist.most_common(10)),
                'product_distribution': dict(product_dist),
                'decision_distribution': dict(decision_dist),
                'key_insights': self._generate_production_insights(data, avg_risk, high_risk_orders, total_orders)
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Production analysis error: {e}")
            return {'error': str(e)}
    
    def _analyze_quality(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze quality data"""
        try:
            base_query = """
            SELECT q.*, qr.inspection_id, qr.total_defects, qr.critical_defects, 
                   qr.major_defects, qr.minor_defects, qr.defect_rate, qr.pass_fail
            FROM quality q
            LEFT JOIN quality_result qr ON q.batch_id = qr.batch_id
            """
            
            where_conditions = []
            params = []
            
            if filters:
                if filters.get('product_type'):
                    where_conditions.append("q.product_type = ?")
                    params.append(filters['product_type'])
                if filters.get('inspection_standard'):
                    where_conditions.append("q.inspection_standard = ?")
                    params.append(filters['inspection_standard'])
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            data = self.db_manager.query(base_query, tuple(params))
            
            if not data:
                return {'error': 'No quality data found'}
            
            # Analysis
            total_batches = len(data)
            product_dist = Counter(row['product_type'] for row in data if row['product_type'])
            standard_dist = Counter(row['inspection_standard'] for row in data if row['inspection_standard'])
            
            # Defect analysis
            defect_rates = [row['defect_rate'] for row in data if row['defect_rate'] is not None]
            avg_defect_rate = statistics.mean(defect_rates) if defect_rates else 0
            
            total_defects = sum(row['total_defects'] for row in data if row['total_defects'])
            critical_defects = sum(row['critical_defects'] for row in data if row['critical_defects'])
            major_defects = sum(row['major_defects'] for row in data if row['major_defects'])
            minor_defects = sum(row['minor_defects'] for row in data if row['minor_defects'])
            
            # Pass/Fail analysis
            pass_fail_dist = Counter(row['pass_fail'] for row in data if row['pass_fail'])
            pass_rate = (pass_fail_dist.get('PASS', 0) / total_batches * 100) if total_batches > 0 else 0
            
            insights = {
                'total_batches': total_batches,
                'average_defect_rate': round(avg_defect_rate, 2),
                'total_defects': total_defects,
                'critical_defects': critical_defects,
                'major_defects': major_defects,
                'minor_defects': minor_defects,
                'pass_rate': round(pass_rate, 2),
                'product_distribution': dict(product_dist),
                'standard_distribution': dict(standard_dist),
                'pass_fail_distribution': dict(pass_fail_dist),
                'key_insights': self._generate_quality_insights(data, avg_defect_rate, pass_rate, critical_defects)
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Quality analysis error: {e}")
            return {'error': str(e)}
    
    def _analyze_quotation(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze quotation data"""
        try:
            base_query = """
            SELECT q.*, qr.quote_id, qr.material_cost, qr.production_cost, 
                   qr.quality_cost, qr.risk_premium, qr.total_amount
            FROM quotation q
            LEFT JOIN quotation_result qr ON q.quote_request_id = qr.request_id
            """
            
            where_conditions = []
            params = []
            
            if filters:
                if filters.get('customer'):
                    where_conditions.append("q.customer LIKE ?")
                    params.append(f"%{filters['customer']}%")
                if filters.get('priority'):
                    where_conditions.append("q.priority = ?")
                    params.append(filters['priority'])
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            data = self.db_manager.query(base_query, tuple(params))
            
            if not data:
                return {'error': 'No quotation data found'}
            
            # Analysis
            total_quotes = len(data)
            customer_dist = Counter(row['customer'] for row in data if row['customer'])
            product_dist = Counter(row['product_type'] for row in data if row['product_type'])
            priority_dist = Counter(row['priority'] for row in data if row['priority'])
            
            # Cost analysis
            total_amounts = [row['total_amount'] for row in data if row['total_amount']]
            total_revenue = sum(total_amounts)
            avg_quote_value = statistics.mean(total_amounts) if total_amounts else 0
            
            material_costs = [row['material_cost'] for row in data if row['material_cost']]
            avg_material_cost = statistics.mean(material_costs) if material_costs else 0
            
            insights = {
                'total_quotes': total_quotes,
                'total_revenue': round(total_revenue, 2),
                'average_quote_value': round(avg_quote_value, 2),
                'average_material_cost': round(avg_material_cost, 2),
                'customer_distribution': dict(customer_dist.most_common(10)),
                'product_distribution': dict(product_dist),
                'priority_distribution': dict(priority_dist),
                'key_insights': self._generate_quotation_insights(data, avg_quote_value, total_revenue)
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Quotation analysis error: {e}")
            return {'error': str(e)}
    
    def _analyze_invoice(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze invoice data"""
        try:
            base_query = """
            SELECT i.*, ir.invoice_number, ir.invoice_date, ir.due_date, ir.total_amount
            FROM invoice i
            LEFT JOIN invoice_result ir ON i.invoice_request_id = ir.request_id
            """
            
            data = self.db_manager.query(base_query)
            
            if not data:
                return {'error': 'No invoice data found'}
            
            # Analysis
            total_invoices = len(data)
            customer_dist = Counter(row['customer_name'] for row in data if row['customer_name'])
            
            # Amount analysis
            amounts = [row['total_amount'] for row in data if row['total_amount']]
            total_invoiced = sum(amounts)
            avg_invoice_value = statistics.mean(amounts) if amounts else 0
            
            insights = {
                'total_invoices': total_invoices,
                'total_invoiced': round(total_invoiced, 2),
                'average_invoice_value': round(avg_invoice_value, 2),
                'customer_distribution': dict(customer_dist.most_common(10)),
                'key_insights': self._generate_invoice_insights(data, avg_invoice_value, total_invoiced)
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Invoice analysis error: {e}")
            return {'error': str(e)}
    
    def _analyze_rnd(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze R&D data"""
        try:
            base_query = """
            SELECT r.*, rr.formulation_id, rr.base_polymer, rr.cost_per_kg, 
                   rr.ul94_rating, rr.tensile_mpa, rr.rohs_compliant, rr.reach_compliant
            FROM rnd r
            LEFT JOIN rnd_result rr ON r.request_id = rr.request_id
            """
            
            data = self.db_manager.query(base_query)
            
            if not data:
                return {'error': 'No R&D data found'}
            
            # Analysis
            total_requests = len(data)
            application_dist = Counter(row['application'] for row in data if row['application'])
            standards_dist = Counter(row['standards'] for row in data if row['standards'])
            polymer_dist = Counter(row['base_polymer'] for row in data if row['base_polymer'])
            
            # Cost analysis
            costs = [row['cost_per_kg'] for row in data if row['cost_per_kg']]
            avg_cost = statistics.mean(costs) if costs else 0
            
            # Compliance analysis
            rohs_compliant = len([r for r in data if r.get('rohs_compliant') == 'Yes'])
            reach_compliant = len([r for r in data if r.get('reach_compliant') == 'Yes'])
            
            insights = {
                'total_requests': total_requests,
                'average_cost_per_kg': round(avg_cost, 2),
                'rohs_compliance_rate': round((rohs_compliant / total_requests * 100), 2) if total_requests > 0 else 0,
                'reach_compliance_rate': round((reach_compliant / total_requests * 100), 2) if total_requests > 0 else 0,
                'application_distribution': dict(application_dist),
                'standards_distribution': dict(standards_dist),
                'polymer_distribution': dict(polymer_dist),
                'key_insights': self._generate_rnd_insights(data, avg_cost, rohs_compliant, reach_compliant)
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"R&D analysis error: {e}")
            return {'error': str(e)}
    
    def _cross_analysis(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform cross-entity analysis"""
        try:
            # Production vs Quality correlation
            prod_quality_query = """
            SELECT p.order_id, p.priority, p.product_type, p.customer,
                   qr.defect_rate, qr.pass_fail
            FROM production p
            JOIN quality q ON p.product_type = q.product_type
            JOIN quality_result qr ON q.batch_id = qr.batch_id
            """
            
            prod_quality_data = self.db_manager.query(prod_quality_query)
            
            # Quotation vs Invoice correlation
            quote_invoice_query = """
            SELECT qr.total_amount as quote_amount, ir.total_amount as invoice_amount,
                   q.customer, q.product_type
            FROM quotation q
            JOIN quotation_result qr ON q.quote_request_id = qr.request_id
            JOIN invoice i ON qr.quote_id = i.quote_id
            JOIN invoice_result ir ON i.invoice_request_id = ir.request_id
            """
            
            quote_invoice_data = self.db_manager.query(quote_invoice_query)
            
            insights = {
                'production_quality_correlation': self._analyze_prod_quality_correlation(prod_quality_data),
                'quote_invoice_accuracy': self._analyze_quote_invoice_accuracy(quote_invoice_data),
                'key_insights': ['Cross-entity analysis provides comprehensive business intelligence']
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Cross analysis error: {e}")
            return {'error': str(e)}
    
    def _generate_production_insights(self, data: List[Dict], avg_risk: float, high_risk: int, total: int) -> List[str]:
        """Generate production insights"""
        insights = []
        
        if avg_risk > 3:
            insights.append(f"⚠️ Average risk score is {avg_risk:.1f}, indicating potential production challenges")
        
        if high_risk > 0:
            insights.append(f"🔴 {high_risk} out of {total} orders ({high_risk/total*100:.1f}%) are high-risk")
        
        priority_counts = Counter(row['priority'] for row in data if row['priority'])
        if priority_counts.get('critical', 0) > 0:
            insights.append(f"⚡ {priority_counts['critical']} critical priority orders require immediate attention")
        
        return insights
    
    def _generate_quality_insights(self, data: List[Dict], avg_defect: float, pass_rate: float, critical: int) -> List[str]:
        """Generate quality insights"""
        insights = []
        
        if avg_defect > 5:
            insights.append(f"⚠️ Average defect rate is {avg_defect:.1f}%, above acceptable threshold")
        
        if pass_rate < 95:
            insights.append(f"🔴 Pass rate is {pass_rate:.1f}%, below target of 95%")
        
        if critical > 0:
            insights.append(f"🚨 {critical} critical defects found - immediate action required")
        
        return insights
    
    def _generate_quotation_insights(self, data: List[Dict], avg_value: float, total_revenue: float) -> List[str]:
        """Generate quotation insights"""
        insights = []
        
        insights.append(f"💰 Total potential revenue: ₹{total_revenue:,.2f}")
        insights.append(f"📊 Average quotation value: ₹{avg_value:,.2f}")
        
        return insights
    
    def _generate_invoice_insights(self, data: List[Dict], avg_value: float, total_invoiced: float) -> List[str]:
        """Generate invoice insights"""
        insights = []
        
        insights.append(f"💵 Total invoiced amount: ₹{total_invoiced:,.2f}")
        insights.append(f"📈 Average invoice value: ₹{avg_value:,.2f}")
        
        return insights
    
    def _generate_rnd_insights(self, data: List[Dict], avg_cost: float, rohs: int, reach: int) -> List[str]:
        """Generate R&D insights"""
        insights = []
        
        insights.append(f"🧪 Average formulation cost: ₹{avg_cost:.2f}/kg")
        insights.append(f"✅ RoHS compliance: {rohs} formulations")
        insights.append(f"✅ REACH compliance: {reach} formulations")
        
        return insights
    
    def _analyze_prod_quality_correlation(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze production-quality correlation"""
        if not data:
            return {}
        
        priority_defects = defaultdict(list)
        for row in data:
            if row['priority'] and row['defect_rate'] is not None:
                priority_defects[row['priority']].append(row['defect_rate'])
        
        correlation = {}
        for priority, defects in priority_defects.items():
            correlation[priority] = {
                'avg_defect_rate': round(statistics.mean(defects), 2),
                'sample_size': len(defects)
            }
        
        return correlation
    
    def _analyze_quote_invoice_accuracy(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze quotation vs invoice accuracy"""
        if not data:
            return {}
        
        accuracies = []
        for row in data:
            if row['quote_amount'] and row['invoice_amount']:
                accuracy = abs(row['quote_amount'] - row['invoice_amount']) / row['quote_amount'] * 100
                accuracies.append(accuracy)
        
        return {
            'average_variance': round(statistics.mean(accuracies), 2) if accuracies else 0,
            'sample_size': len(accuracies)
        }
    
    def generate_analysis(self, analysis_type: str, filters: Dict[str, Any] = None, use_cache: bool = True) -> Dict[str, Any]:
        """Generate analysis with caching"""
        if analysis_type not in self.analysis_templates:
            return {'error': f'Unknown analysis type: {analysis_type}'}
        
        filters = filters or {}
        cache_key = self._generate_cache_key(analysis_type, filters)
        cache_table = f"{analysis_type}_reports_cache"
        
        # Check cache first
        if use_cache and analysis_type != 'cross_analysis':
            cached = self._get_cached_analysis(cache_table, cache_key)
            if cached:
                self.logger.info(f"Returning cached analysis for {analysis_type}")
                return cached
        
        # Generate new analysis
        self.logger.info(f"Generating new analysis for {analysis_type}")
        analysis_func = self.analysis_templates[analysis_type]
        insights = analysis_func(filters)
        
        # Cache results (except for cross analysis which uses multiple tables)
        if analysis_type != 'cross_analysis' and 'error' not in insights:
            content = json.dumps(insights, indent=2)
            self._cache_analysis(cache_table, cache_key, filters, content, insights)
        
        insights['cached'] = False
        insights['created_at'] = datetime.now().isoformat()
        
        return insights