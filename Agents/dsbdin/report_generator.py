#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_analyzer import AIAnalyzer
from database_manager import DatabaseManager
from datetime import datetime
import json
from typing import Dict, List, Any, Optional
import logging

class ReportGenerator:
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
        self.db_manager = DatabaseManager()
        self.logger = self._setup_logger()
        
        # Report templates
        self.templates = {
            'production': self._generate_production_report,
            'quality': self._generate_quality_report,
            'quotation': self._generate_quotation_report,
            'invoice': self._generate_invoice_report,
            'rnd': self._generate_rnd_report,
            'comprehensive': self._generate_comprehensive_report,
            'audit': self._generate_audit_report
        }
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('ReportGenerator')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _format_number(self, value: float, currency: bool = False) -> str:
        """Format numbers with proper formatting"""
        if value is None:
            return "N/A"
        
        if currency:
            return f"₹{value:,.2f}"
        else:
            return f"{value:,.2f}"
    
    def _format_percentage(self, value: float) -> str:
        """Format percentage values"""
        if value is None:
            return "N/A"
        return f"{value:.1f}%"
    
    def _generate_header(self, title: str, subtitle: str = None) -> str:
        """Generate report header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"""# {title}

**Generated:** {timestamp}
**System:** Manufacturing Audit Intelligence Platform
"""
        if subtitle:
            header += f"**Analysis:** {subtitle}\n"
        
        header += "\n---\n\n"
        return header
    
    def _generate_summary_section(self, insights: Dict[str, Any]) -> str:
        """Generate executive summary section"""
        summary = "## Executive Summary\n\n"
        
        if 'key_insights' in insights and insights['key_insights']:
            summary += "### Key Insights\n\n"
            for insight in insights['key_insights']:
                summary += f"- {insight}\n"
            summary += "\n"
        
        return summary
    
    def _generate_metrics_table(self, metrics: Dict[str, Any], title: str = "Key Metrics") -> str:
        """Generate metrics table"""
        table = f"### {title}\n\n"
        table += "| Metric | Value |\n"
        table += "|--------|-------|\n"
        
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                if 'cost' in key.lower() or 'amount' in key.lower() or 'revenue' in key.lower():
                    formatted_value = self._format_number(value, currency=True)
                elif 'rate' in key.lower() and value <= 100:
                    formatted_value = self._format_percentage(value)
                else:
                    formatted_value = self._format_number(value)
            else:
                formatted_value = str(value)
            
            # Format key for display
            display_key = key.replace('_', ' ').title()
            table += f"| {display_key} | {formatted_value} |\n"
        
        table += "\n"
        return table
    
    def _generate_distribution_chart(self, distribution: Dict[str, Any], title: str) -> str:
        """Generate distribution visualization"""
        if not distribution:
            return ""
        
        chart = f"### {title}\n\n"
        
        # Sort by value descending
        sorted_items = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        
        chart += "| Category | Count | Percentage |\n"
        chart += "|----------|-------|------------|\n"
        
        total = sum(distribution.values())
        for category, count in sorted_items[:10]:  # Top 10
            percentage = (count / total * 100) if total > 0 else 0
            chart += f"| {category} | {count} | {percentage:.1f}% |\n"
        
        chart += "\n"
        return chart
    
    def _generate_production_report(self, filters: Dict[str, Any] = None) -> str:
        """Generate production analysis report"""
        insights = self.ai_analyzer.generate_analysis('production', filters)
        
        if 'error' in insights:
            return f"# Production Report\n\nError: {insights['error']}\n"
        
        report = self._generate_header("Production Analysis Report", "Manufacturing Orders & Execution")
        report += self._generate_summary_section(insights)
        
        # Key metrics
        metrics = {
            'total_orders': insights.get('total_orders', 0),
            'total_quantity': insights.get('total_quantity', 0),
            'average_quantity': insights.get('average_quantity', 0),
            'average_risk_score': insights.get('average_risk_score', 0),
            'high_risk_orders': insights.get('high_risk_orders', 0)
        }
        report += self._generate_metrics_table(metrics, "Production Metrics")
        
        # Distributions
        if insights.get('priority_distribution'):
            report += self._generate_distribution_chart(insights['priority_distribution'], "Priority Distribution")
        
        if insights.get('customer_distribution'):
            report += self._generate_distribution_chart(insights['customer_distribution'], "Top Customers")
        
        if insights.get('product_distribution'):
            report += self._generate_distribution_chart(insights['product_distribution'], "Product Type Distribution")
        
        if insights.get('decision_distribution'):
            report += self._generate_distribution_chart(insights['decision_distribution'], "Production Decisions")
        
        return report
    
    def _generate_quality_report(self, filters: Dict[str, Any] = None) -> str:
        """Generate quality analysis report"""
        insights = self.ai_analyzer.generate_analysis('quality', filters)
        
        if 'error' in insights:
            return f"# Quality Report\n\nError: {insights['error']}\n"
        
        report = self._generate_header("Quality Analysis Report", "Inspection Results & Defect Analysis")
        report += self._generate_summary_section(insights)
        
        # Key metrics
        metrics = {
            'total_batches': insights.get('total_batches', 0),
            'average_defect_rate': insights.get('average_defect_rate', 0),
            'total_defects': insights.get('total_defects', 0),
            'critical_defects': insights.get('critical_defects', 0),
            'major_defects': insights.get('major_defects', 0),
            'minor_defects': insights.get('minor_defects', 0),
            'pass_rate': insights.get('pass_rate', 0)
        }
        report += self._generate_metrics_table(metrics, "Quality Metrics")
        
        # Distributions
        if insights.get('product_distribution'):
            report += self._generate_distribution_chart(insights['product_distribution'], "Product Quality Distribution")
        
        if insights.get('standard_distribution'):
            report += self._generate_distribution_chart(insights['standard_distribution'], "Inspection Standards")
        
        return report
    
    def _generate_quotation_report(self, filters: Dict[str, Any] = None) -> str:
        """Generate quotation analysis report"""
        insights = self.ai_analyzer.generate_analysis('quotation', filters)
        
        if 'error' in insights:
            return f"# Quotation Report\n\nError: {insights['error']}\n"
        
        report = self._generate_header("Quotation Analysis Report", "Sales Quotes & Revenue Analysis")
        report += self._generate_summary_section(insights)
        
        # Key metrics
        metrics = {
            'total_quotes': insights.get('total_quotes', 0),
            'total_revenue': insights.get('total_revenue', 0),
            'average_quote_value': insights.get('average_quote_value', 0),
            'average_material_cost': insights.get('average_material_cost', 0)
        }
        report += self._generate_metrics_table(metrics, "Quotation Metrics")
        
        # Distributions
        if insights.get('customer_distribution'):
            report += self._generate_distribution_chart(insights['customer_distribution'], "Top Quote Customers")
        
        if insights.get('product_distribution'):
            report += self._generate_distribution_chart(insights['product_distribution'], "Quoted Products")
        
        if insights.get('priority_distribution'):
            report += self._generate_distribution_chart(insights['priority_distribution'], "Quote Priority Distribution")
        
        return report
    
    def _generate_invoice_report(self, filters: Dict[str, Any] = None) -> str:
        """Generate invoice analysis report"""
        insights = self.ai_analyzer.generate_analysis('invoice', filters)
        
        if 'error' in insights:
            return f"# Invoice Report\n\nError: {insights['error']}\n"
        
        report = self._generate_header("Invoice Analysis Report", "Billing & Revenue Tracking")
        report += self._generate_summary_section(insights)
        
        # Key metrics
        metrics = {
            'total_invoices': insights.get('total_invoices', 0),
            'total_invoiced': insights.get('total_invoiced', 0),
            'average_invoice_value': insights.get('average_invoice_value', 0)
        }
        report += self._generate_metrics_table(metrics, "Invoice Metrics")
        
        # Distributions
        if insights.get('customer_distribution'):
            report += self._generate_distribution_chart(insights['customer_distribution'], "Top Invoice Customers")
        
        return report
    
    def _generate_rnd_report(self, filters: Dict[str, Any] = None) -> str:
        """Generate R&D analysis report"""
        insights = self.ai_analyzer.generate_analysis('rnd', filters)
        
        if 'error' in insights:
            return f"# R&D Report\n\nError: {insights['error']}\n"
        
        report = self._generate_header("R&D Analysis Report", "Formulation Development & Compliance")
        report += self._generate_summary_section(insights)
        
        # Key metrics
        metrics = {
            'total_requests': insights.get('total_requests', 0),
            'average_cost_per_kg': insights.get('average_cost_per_kg', 0),
            'rohs_compliance_rate': insights.get('rohs_compliance_rate', 0),
            'reach_compliance_rate': insights.get('reach_compliance_rate', 0)
        }
        report += self._generate_metrics_table(metrics, "R&D Metrics")
        
        # Distributions
        if insights.get('application_distribution'):
            report += self._generate_distribution_chart(insights['application_distribution'], "Application Areas")
        
        if insights.get('standards_distribution'):
            report += self._generate_distribution_chart(insights['standards_distribution'], "Standards Compliance")
        
        if insights.get('polymer_distribution'):
            report += self._generate_distribution_chart(insights['polymer_distribution'], "Base Polymer Usage")
        
        return report
    
    def _generate_comprehensive_report(self, filters: Dict[str, Any] = None) -> str:
        """Generate comprehensive cross-entity report"""
        report = self._generate_header("Comprehensive Manufacturing Report", "Complete Business Intelligence Analysis")
        
        # Get all analyses
        production_insights = self.ai_analyzer.generate_analysis('production', filters)
        quality_insights = self.ai_analyzer.generate_analysis('quality', filters)
        quotation_insights = self.ai_analyzer.generate_analysis('quotation', filters)
        invoice_insights = self.ai_analyzer.generate_analysis('invoice', filters)
        rnd_insights = self.ai_analyzer.generate_analysis('rnd', filters)
        cross_insights = self.ai_analyzer.generate_analysis('cross_analysis', filters)
        
        # Executive summary with key insights from all areas
        report += "## Executive Summary\n\n"
        report += "### Manufacturing Overview\n\n"
        
        all_insights = []
        for insights in [production_insights, quality_insights, quotation_insights, invoice_insights, rnd_insights]:
            if 'key_insights' in insights:
                all_insights.extend(insights['key_insights'])
        
        for insight in all_insights[:10]:  # Top 10 insights
            report += f"- {insight}\n"
        
        report += "\n"
        
        # High-level metrics dashboard
        report += "## Business Dashboard\n\n"
        report += "| Department | Key Metric | Value |\n"
        report += "|------------|------------|-------|\n"
        
        if 'total_orders' in production_insights:
            report += f"| Production | Total Orders | {production_insights['total_orders']} |\n"
        if 'pass_rate' in quality_insights:
            report += f"| Quality | Pass Rate | {self._format_percentage(quality_insights['pass_rate'])} |\n"
        if 'total_revenue' in quotation_insights:
            report += f"| Sales | Potential Revenue | {self._format_number(quotation_insights['total_revenue'], True)} |\n"
        if 'total_invoiced' in invoice_insights:
            report += f"| Finance | Total Invoiced | {self._format_number(invoice_insights['total_invoiced'], True)} |\n"
        if 'total_requests' in rnd_insights:
            report += f"| R&D | Active Projects | {rnd_insights['total_requests']} |\n"
        
        report += "\n"
        
        # Cross-entity correlations
        if cross_insights and 'error' not in cross_insights:
            report += "## Cross-Entity Analysis\n\n"
            
            if 'production_quality_correlation' in cross_insights:
                report += "### Production-Quality Correlation\n\n"
                corr = cross_insights['production_quality_correlation']
                if corr:
                    report += "| Priority Level | Avg Defect Rate | Sample Size |\n"
                    report += "|----------------|-----------------|-------------|\n"
                    for priority, data in corr.items():
                        report += f"| {priority} | {self._format_percentage(data['avg_defect_rate'])} | {data['sample_size']} |\n"
                    report += "\n"
            
            if 'quote_invoice_accuracy' in cross_insights:
                report += "### Quote-Invoice Accuracy\n\n"
                accuracy = cross_insights['quote_invoice_accuracy']
                if accuracy:
                    report += f"- Average variance between quotes and invoices: {self._format_percentage(accuracy['average_variance'])}\n"
                    report += f"- Sample size: {accuracy['sample_size']} transactions\n\n"
        
        return report
    
    def _generate_audit_report(self, filters: Dict[str, Any] = None) -> str:
        """Generate audit-ready compliance report"""
        report = self._generate_header("Manufacturing Audit Report", "Compliance & Regulatory Analysis")
        
        # Get comprehensive data
        comprehensive_data = self._generate_comprehensive_report(filters)
        
        # Add audit-specific sections
        report += "## Audit Compliance Summary\n\n"
        report += "### Data Integrity\n\n"
        
        # Check data completeness
        table_stats = {}
        for table_name in ['production', 'quality', 'quotation', 'invoice', 'rnd']:
            info = self.db_manager.get_table_info(table_name)
            table_stats[table_name] = info.get('row_count', 0)
        
        report += "| Data Source | Record Count | Status |\n"
        report += "|-------------|--------------|--------|\n"
        
        for table, count in table_stats.items():
            status = "✅ Complete" if count > 0 else "⚠️ No Data"
            report += f"| {table.title()} | {count} | {status} |\n"
        
        report += "\n"
        
        # Add comprehensive analysis
        report += comprehensive_data.split("## Business Dashboard")[1] if "## Business Dashboard" in comprehensive_data else ""
        
        # Audit trail
        report += "## Audit Trail\n\n"
        report += f"- Report generated: {datetime.now().isoformat()}\n"
        report += f"- Data sources: Google Sheets (16 tabs)\n"
        report += f"- Analysis engine: AI-powered cross-entity correlation\n"
        report += f"- Compliance standards: Manufacturing audit requirements\n\n"
        
        return report
    
    def generate_report(self, report_type: str, filters: Dict[str, Any] = None, 
                       save_to_file: bool = True) -> Dict[str, Any]:
        """Generate report and optionally save to file"""
        if report_type not in self.templates:
            return {'error': f'Unknown report type: {report_type}'}
        
        try:
            # Generate report content
            report_func = self.templates[report_type]
            content = report_func(filters)
            
            result = {
                'report_type': report_type,
                'content': content,
                'generated_at': datetime.now().isoformat(),
                'filters': filters or {}
            }
            
            # Save to file if requested
            if save_to_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"../reports/{report_type}_report_{timestamp}.md"
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    result['saved_to'] = filename
                    self.logger.info(f"Report saved to {filename}")
                except Exception as e:
                    self.logger.error(f"Failed to save report: {e}")
                    result['save_error'] = str(e)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return {'error': str(e)}
    
    def list_available_reports(self) -> List[str]:
        """List all available report types"""
        return list(self.templates.keys())