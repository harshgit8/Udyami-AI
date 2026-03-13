from datetime import datetime
import config
from sheets_client import SheetsClient
from ai_client import AIClient
from agents.invoice_agent import InvoiceAgent

class InvoiceOrchestrator:
    def __init__(self):
        self.sheets_client = SheetsClient()
        self.ai_client = AIClient()
        self.invoice_agent = InvoiceAgent(self.ai_client)
    
    def run(self):
        print("Starting Invoice Orchestration...")
        
        print("\n[1/3] Reading invoice requests from Google Sheets (Invoice tab)...")
        try:
            raw_rows = self.sheets_client.read_sheet("Invoice!A:AB")
        except Exception as e:
            print(f"  Error: {e}")
            print("  Make sure 'Invoice' sheet tab exists with invoice requests")
            return
        
        if not raw_rows or len(raw_rows) < 2:
            print("  No data found in Invoice sheet")
            return
        
        headers = raw_rows[0]
        data_rows = raw_rows[1:]
        
        print(f"  Found {len(data_rows)} invoice requests")
        
        print("\n[2/3] Processing invoice requests...")
        results = []
        
        for idx, row in enumerate(data_rows, 1):
            if len(row) < 20:
                print(f"  Skipping row {idx}: insufficient data")
                continue
            
            invoice_request = {
                'invoice_request_id': row[0] if len(row) > 0 else f"INV-REQ-{idx}",
                'customer_name': row[1] if len(row) > 1 else "",
                'customer_address': row[2] if len(row) > 2 else "",
                'customer_gstin': row[3] if len(row) > 3 else "",
                'quote_id': row[4] if len(row) > 4 else "",
                'order_id': row[5] if len(row) > 5 else "",
                'po_number': row[6] if len(row) > 6 else "",
                'product_type': row[7] if len(row) > 7 else "",
                'product_description': row[8] if len(row) > 8 else "",
                'quantity_ordered': int(row[9]) if len(row) > 9 and row[9] else 0,
                'quantity_delivered': int(row[10]) if len(row) > 10 and row[10] else 0,
                'hsn_code': row[11] if len(row) > 11 else "39169099",
                'batch_id': row[12] if len(row) > 12 else "",
                'inspection_id': row[13] if len(row) > 13 else "",
                'quality_decision': row[14] if len(row) > 14 else "ACCEPT",
                'formulation_id': row[15] if len(row) > 15 else "",
                'material_cost': float(row[16]) if len(row) > 16 and row[16] else 0,
                'production_cost': float(row[17]) if len(row) > 17 and row[17] else 0,
                'quality_cost': float(row[18]) if len(row) > 18 and row[18] else 0,
                'packaging_cost': float(row[19]) if len(row) > 19 and row[19] else 0,
                'subtotal': float(row[20]) if len(row) > 20 and row[20] else 0,
                'advance_paid': float(row[21]) if len(row) > 21 and row[21] else 0,
                'discount': float(row[22]) if len(row) > 22 and row[22] else 0,
                'additional_charges': float(row[23]) if len(row) > 23 and row[23] else 0,
                'delivery_date': row[24] if len(row) > 24 else "",
                'delivery_challan': row[25] if len(row) > 25 else "",
                'transport_details': row[26] if len(row) > 26 else "",
                'payment_terms': row[27] if len(row) > 27 else "30 days"
            }
            
            print(f"  Generating invoice: {invoice_request['invoice_request_id']} - {invoice_request['customer_name']}")
            
            try:
                invoice_result = self.invoice_agent.generate_invoice(invoice_request)
                results.append(invoice_result)
                print(f"    ✓ Invoice: {invoice_result['invoice_number']} - Total: ₹{round(invoice_result['grand_total'], 2)} - Due: ₹{round(invoice_result['payment_details']['balance_due'], 2)}")
            except Exception as e:
                print(f"    ✗ Error: {e}")
                results.append({
                    'invoice_request_id': invoice_request['invoice_request_id'],
                    'customer_name': invoice_request['customer_name'],
                    'error': str(e),
                    'invoice_number': 'ERROR',
                    'grand_total': 0
                })
        
        print(f"\n[3/3] Writing results to Google Sheets (InvoiceResult tab)...")
        self._write_results_to_sheet(results)
        
        report_file = f"{config.REPORTS_DIR}/invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self._save_detailed_report(results, report_file)
        print(f"  Detailed report saved: {report_file}")
        
        print("\n✓ Invoice Orchestration complete!")
        return results
    
    def _write_results_to_sheet(self, results):
        try:
            output_rows = [[
                'Invoice Number',
                'Invoice Date',
                'Due Date',
                'Request ID',
                'Customer Name',
                'Customer GSTIN',
                'Order ID',
                'PO Number',
                'Product',
                'Quantity',
                'Subtotal (₹)',
                'Adjustments (₹)',
                'Taxable Amount (₹)',
                'Tax Type',
                'CGST (₹)',
                'SGST (₹)',
                'IGST (₹)',
                'Total Tax (₹)',
                'Grand Total (₹)',
                'Advance Paid (₹)',
                'Balance Due (₹)',
                'Payment Terms',
                'Delivery Date',
                'Delivery Challan'
            ]]
            
            for result in results:
                if 'error' in result:
                    output_rows.append([
                        'ERROR',
                        '',
                        '',
                        result['invoice_request_id'],
                        result['customer_name'],
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
                        '',
                        '',
                        '',
                        f"Error: {result['error']}"
                    ])
                    continue
                
                output_rows.append([
                    result['invoice_number'],
                    result['invoice_date'],
                    result['due_date'],
                    result['invoice_request_id'],
                    result['customer_details']['name'],
                    result['customer_details']['gstin'],
                    result['reference_documents']['order_id'],
                    result['reference_documents']['po_number'],
                    result['product_details']['description'],
                    str(result['product_details']['quantity_delivered']),
                    str(round(result['cost_breakdown']['subtotal'], 2)),
                    str(round(result['adjustments']['total'], 2)),
                    str(round(result['adjusted_amount'], 2)),
                    result['tax_details']['tax_type'],
                    str(round(result['tax_details']['cgst'], 2)),
                    str(round(result['tax_details']['sgst'], 2)),
                    str(round(result['tax_details']['igst'], 2)),
                    str(round(result['tax_details']['total_tax'], 2)),
                    str(round(result['grand_total'], 2)),
                    str(round(result['payment_details']['advance_paid'], 2)),
                    str(round(result['payment_details']['balance_due'], 2)),
                    result['payment_details']['payment_terms'],
                    result['delivery_details']['delivery_date'],
                    result['delivery_details']['delivery_challan']
                ])
            
            self.sheets_client.write_sheet('InvoiceResult!A:X', output_rows)
            print(f"  ✓ Results written to 'InvoiceResult' tab ({len(output_rows)-1} invoices)")
        
        except Exception as e:
            print(f"  ✗ Error writing to sheet: {e}")
    
    def _save_detailed_report(self, results, filename):
        lines = []
        lines.append("# 📄 Invoice Batch Report")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total Invoices:** {len(results)}\n")
        
        total_invoiced = sum(r.get('grand_total', 0) for r in results if 'error' not in r)
        total_balance = sum(r.get('payment_details', {}).get('balance_due', 0) for r in results if 'error' not in r)
        
        lines.append(f"**Total Invoiced Value:** ₹{round(total_invoiced, 2)}")
        lines.append(f"**Total Balance Due:** ₹{round(total_balance, 2)}\n")
        lines.append("="*80 + "\n")
        
        for result in results:
            if 'error' in result:
                lines.append(f"## ❌ {result['invoice_request_id']} - {result['customer_name']} - ERROR")
                lines.append(f"**Error:** {result['error']}\n")
                lines.append("="*80 + "\n")
                continue
            
            report = self.invoice_agent.generate_report(result)
            lines.append(report)
            lines.append("\n" + "="*80 + "\n")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

if __name__ == '__main__':
    orchestrator = InvoiceOrchestrator()
    orchestrator.run()
