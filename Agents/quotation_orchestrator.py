from datetime import datetime
import config
from sheets_client import SheetsClient
from ai_client import AIClient
from agents.quotation_agent import QuotationAgent

class QuotationOrchestrator:
    def __init__(self):
        self.sheets_client = SheetsClient()
        self.ai_client = AIClient()
        self.quotation_agent = QuotationAgent(self.ai_client)
    
    def run(self):
        print("Starting Quotation Orchestration...")
        
        print("\n[1/3] Reading quotation requests from Google Sheets (Quotation tab)...")
        try:
            raw_rows = self.sheets_client.read_sheet("Quotation!A:T")
        except Exception as e:
            print(f"  Error: {e}")
            print("  Make sure 'Quotation' sheet tab exists with quote requests")
            return
        
        if not raw_rows or len(raw_rows) < 2:
            print("  No data found in Quotation sheet")
            return
        
        headers = raw_rows[0]
        data_rows = raw_rows[1:]
        
        print(f"  Found {len(data_rows)} quotation requests")
        
        print("\n[2/3] Processing quotation requests...")
        results = []
        
        for idx, row in enumerate(data_rows, 1):
            if len(row) < 10:
                print(f"  Skipping row {idx}: insufficient data")
                continue
            
            quote_request = {
                'quote_request_id': row[0] if len(row) > 0 else f"QR_{idx}",
                'customer': row[1] if len(row) > 1 else "",
                'product_type': row[2] if len(row) > 2 else "",
                'quantity': int(row[3]) if len(row) > 3 and row[3] else 0,
                'application': row[4] if len(row) > 4 else "",
                'quality_standard': row[5] if len(row) > 5 else "ISO_2859",
                'priority': row[6] if len(row) > 6 else "normal",
                'delivery_required': row[7] if len(row) > 7 else "",
                'special_requirements': row[8] if len(row) > 8 else "",
                'material_formulation': row[9] if len(row) > 9 else "",
                'material_cost_per_kg': float(row[10]) if len(row) > 10 and row[10] else 80,
                'weight_per_unit_kg': float(row[11]) if len(row) > 11 and row[11] else 0.5,
                'ul94_rating': row[12] if len(row) > 12 else "HB",
                'compliance': row[13] if len(row) > 13 else "",
                'machine': row[14] if len(row) > 14 else "M1",
                'production_rate': float(row[15]) if len(row) > 15 and row[15] else 10,
                'setup_time_hours': float(row[16]) if len(row) > 16 and row[16] else 1.5,
                'inspection_standard': row[17] if len(row) > 17 else "ISO_2859",
                'quality_level': row[18] if len(row) > 18 else "GOOD",
                'risk_level': row[19] if len(row) > 19 else "Low"
            }
            
            print(f"  Generating quote: {quote_request['quote_request_id']} - {quote_request['customer']}")
            
            try:
                quotation_result = self.quotation_agent.generate_quotation(quote_request)
                results.append(quotation_result)
                print(f"    ✓ Quote ID: {quotation_result['quote_id']} - Total: ₹{round(quotation_result['grand_total'], 2)}")
            except Exception as e:
                print(f"    ✗ Error: {e}")
                results.append({
                    'quote_request_id': quote_request['quote_request_id'],
                    'customer': quote_request['customer'],
                    'error': str(e),
                    'quote_id': 'ERROR',
                    'grand_total': 0
                })
        
        print(f"\n[3/3] Writing results to Google Sheets (QuotationResult tab)...")
        self._write_results_to_sheet(results)
        
        report_file = f"{config.REPORTS_DIR}/quotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self._save_detailed_report(results, report_file)
        print(f"  Detailed report saved: {report_file}")
        
        print("\n✓ Quotation Orchestration complete!")
        return results
    
    def _write_results_to_sheet(self, results):
        try:
            output_rows = [[
                'Quote ID',
                'Request ID',
                'Customer',
                'Product',
                'Quantity',
                'Material Cost (₹)',
                'Production Cost (₹)',
                'Quality Cost (₹)',
                'Risk Premium (₹)',
                'Subtotal (₹)',
                'Profit Margin %',
                'Profit Amount (₹)',
                'Total Before Tax (₹)',
                'GST (₹)',
                'Grand Total (₹)',
                'Unit Price (₹)',
                'Lead Time (days)',
                'Valid Until',
                'Payment Terms'
            ]]
            
            for result in results:
                if 'error' in result:
                    output_rows.append([
                        'ERROR',
                        result['quote_request_id'],
                        result['customer'],
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        f"Error: {result['error']}"
                    ])
                    continue
                
                output_rows.append([
                    result['quote_id'],
                    result['quote_request_id'],
                    result['customer'],
                    result['product_type'],
                    str(result['quantity']),
                    str(round(result['material_cost']['total'], 2)),
                    str(round(result['production_cost']['total'], 2)),
                    str(round(result['quality_cost']['total'], 2)),
                    str(round(result['risk_premium']['total'], 2)),
                    str(round(result['subtotal'], 2)),
                    str(round(result['profit_margin']['percent'], 2)),
                    str(round(result['profit_margin']['amount'], 2)),
                    str(round(result['total_before_tax'], 2)),
                    str(round(result['gst'], 2)),
                    str(round(result['grand_total'], 2)),
                    str(round(result['unit_price'], 2)),
                    str(result['lead_time_days']),
                    result['valid_until'],
                    result['payment_terms']
                ])
            
            self.sheets_client.write_sheet('QuotationResult!A:S', output_rows)
            print(f"  ✓ Results written to 'QuotationResult' tab ({len(output_rows)-1} quotations)")
        
        except Exception as e:
            print(f"  ✗ Error writing to sheet: {e}")
    
    def _save_detailed_report(self, results, filename):
        lines = []
        lines.append("# 💰 Quotation Batch Report")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total Quotations:** {len(results)}\n")
        
        total_value = sum(r.get('grand_total', 0) for r in results if 'error' not in r)
        lines.append(f"**Total Quoted Value:** ₹{round(total_value, 2)}\n")
        lines.append("="*80 + "\n")
        
        for result in results:
            if 'error' in result:
                lines.append(f"## ❌ {result['quote_request_id']} - {result['customer']} - ERROR")
                lines.append(f"**Error:** {result['error']}\n")
                lines.append("="*80 + "\n")
                continue
            
            report = self.quotation_agent.generate_report(result)
            lines.append(report)
            lines.append("\n" + "="*80 + "\n")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

if __name__ == '__main__':
    orchestrator = QuotationOrchestrator()
    orchestrator.run()
