import json
from datetime import datetime, timedelta

class InvoiceAgent:
    def __init__(self, gemini_client):
        self.gemini = gemini_client
        self.company_details = self._init_company_details()
        self.state_codes = self._init_state_codes()
        self.gst_rates = self._init_gst_rates()
    
    def generate_invoice(self, invoice_request):
        """
        Generate comprehensive invoice based on quotation, production, and quality data.
        
        Args:
            invoice_request (dict): {
                'invoice_request_id': str,
                'customer_name': str,
                'customer_address': str,
                'customer_gstin': str,
                'quote_id': str,
                'order_id': str,
                'po_number': str,
                'product_type': str,
                'product_description': str,
                'quantity_ordered': int,
                'quantity_delivered': int,
                'hsn_code': str,
                'batch_id': str,
                'inspection_id': str,
                'quality_decision': str,
                'formulation_id': str,
                'material_cost': float,
                'production_cost': float,
                'quality_cost': float,
                'packaging_cost': float,
                'subtotal': float,
                'advance_paid': float,
                'discount': float,
                'additional_charges': float,
                'delivery_date': str,
                'delivery_challan': str,
                'transport_details': str,
                'payment_terms': str
            }
        
        Returns:
            dict: Complete invoice with tax calculations and payment details
        """
        customer_state = self._extract_state_from_gstin(invoice_request['customer_gstin'])
        company_state = self._extract_state_from_gstin(self.company_details['gstin'])
        
        is_interstate = customer_state != company_state
        
        base_amount = invoice_request['subtotal']
        adjustments = self._calculate_adjustments(invoice_request)
        adjusted_amount = base_amount + adjustments['total']
        
        tax_details = self._calculate_tax(adjusted_amount, is_interstate, invoice_request['hsn_code'])
        
        grand_total = adjusted_amount + tax_details['total_tax']
        balance_due = grand_total - invoice_request['advance_paid']
        
        due_date = self._calculate_due_date(invoice_request['payment_terms'])
        
        ai_enhanced = self._enhance_with_ai_insights(invoice_request, {
            'adjusted_amount': adjusted_amount,
            'tax_details': tax_details,
            'grand_total': grand_total,
            'balance_due': balance_due
        })
        
        return {
            'invoice_number': self._generate_invoice_number(),
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
            'due_date': due_date,
            'invoice_request_id': invoice_request['invoice_request_id'],
            'company_details': self.company_details,
            'customer_details': {
                'name': invoice_request['customer_name'],
                'address': invoice_request['customer_address'],
                'gstin': invoice_request['customer_gstin'],
                'state': customer_state,
                'state_code': invoice_request['customer_gstin'][:2]
            },
            'reference_documents': {
                'quote_id': invoice_request['quote_id'],
                'order_id': invoice_request['order_id'],
                'po_number': invoice_request['po_number'],
                'batch_id': invoice_request['batch_id'],
                'inspection_id': invoice_request['inspection_id'],
                'formulation_id': invoice_request['formulation_id']
            },
            'product_details': {
                'product_type': invoice_request['product_type'],
                'description': invoice_request['product_description'],
                'hsn_code': invoice_request['hsn_code'],
                'quantity_ordered': invoice_request['quantity_ordered'],
                'quantity_delivered': invoice_request['quantity_delivered'],
                'unit_price': round(base_amount / invoice_request['quantity_delivered'], 2),
                'quality_decision': invoice_request['quality_decision']
            },
            'cost_breakdown': {
                'material_cost': invoice_request['material_cost'],
                'production_cost': invoice_request['production_cost'],
                'quality_cost': invoice_request['quality_cost'],
                'packaging_cost': invoice_request['packaging_cost'],
                'subtotal': base_amount
            },
            'adjustments': adjustments,
            'adjusted_amount': adjusted_amount,
            'tax_details': tax_details,
            'grand_total': grand_total,
            'payment_details': {
                'advance_paid': invoice_request['advance_paid'],
                'balance_due': balance_due,
                'payment_terms': invoice_request['payment_terms'],
                'due_date': due_date
            },
            'delivery_details': {
                'delivery_date': invoice_request['delivery_date'],
                'delivery_challan': invoice_request['delivery_challan'],
                'transport_details': invoice_request['transport_details']
            },
            'bank_details': self.company_details['bank_details'],
            'ai_insights': ai_enhanced
        }
    
    def _init_company_details(self):
        return {
            'name': 'ABC Manufacturing Pvt Ltd',
            'address': '456 Factory Road, Pune, Maharashtra 411001',
            'gstin': '27AABCA1234B1Z5',
            'pan': 'AABCA1234B',
            'contact': '+91-9123456789',
            'email': 'accounts@abcmfg.com',
            'website': 'www.abcmfg.com',
            'bank_details': {
                'bank_name': 'HDFC Bank',
                'account_number': '50200012345678',
                'ifsc_code': 'HDFC0001234',
                'branch': 'Pune Main Branch',
                'account_type': 'Current Account'
            }
        }
    
    def _init_state_codes(self):
        return {
            '01': 'Jammu and Kashmir', '02': 'Himachal Pradesh', '03': 'Punjab',
            '04': 'Chandigarh', '05': 'Uttarakhand', '06': 'Haryana',
            '07': 'Delhi', '08': 'Rajasthan', '09': 'Uttar Pradesh',
            '10': 'Bihar', '11': 'Sikkim', '12': 'Arunachal Pradesh',
            '13': 'Nagaland', '14': 'Manipur', '15': 'Mizoram',
            '16': 'Tripura', '17': 'Meghalaya', '18': 'Assam',
            '19': 'West Bengal', '20': 'Jharkhand', '21': 'Odisha',
            '22': 'Chhattisgarh', '23': 'Madhya Pradesh', '24': 'Gujarat',
            '26': 'Dadra and Nagar Haveli', '27': 'Maharashtra', '29': 'Karnataka',
            '30': 'Goa', '31': 'Lakshadweep', '32': 'Kerala',
            '33': 'Tamil Nadu', '34': 'Puducherry', '35': 'Andaman and Nicobar',
            '36': 'Telangana', '37': 'Andhra Pradesh'
        }
    
    def _init_gst_rates(self):
        return {
            '39169099': 18.0,
            '39173900': 18.0,
            '39174000': 18.0,
            'default': 18.0
        }
    
    def _extract_state_from_gstin(self, gstin):
        if not gstin or len(gstin) < 2:
            return 'Unknown'
        state_code = gstin[:2]
        return self.state_codes.get(state_code, 'Unknown')
    
    def _calculate_adjustments(self, request):
        discount = request.get('discount', 0)
        additional_charges = request.get('additional_charges', 0)
        
        late_delivery_penalty = 0
        quality_bonus = 0
        
        if request.get('quality_decision') == 'ACCEPT' and 'EXCELLENT' in str(request.get('inspection_id', '')):
            quality_bonus = -500
        
        total = additional_charges - discount + late_delivery_penalty + quality_bonus
        
        return {
            'discount': discount,
            'additional_charges': additional_charges,
            'late_delivery_penalty': late_delivery_penalty,
            'quality_bonus': quality_bonus,
            'total': total
        }
    
    def _calculate_tax(self, taxable_amount, is_interstate, hsn_code):
        gst_rate = self.gst_rates.get(hsn_code, self.gst_rates['default'])
        
        if is_interstate:
            igst = taxable_amount * (gst_rate / 100)
            cgst = 0
            sgst = 0
            total_tax = igst
            tax_type = 'IGST'
        else:
            cgst = taxable_amount * (gst_rate / 200)
            sgst = taxable_amount * (gst_rate / 200)
            igst = 0
            total_tax = cgst + sgst
            tax_type = 'CGST+SGST'
        
        return {
            'tax_type': tax_type,
            'gst_rate': gst_rate,
            'cgst': round(cgst, 2),
            'sgst': round(sgst, 2),
            'igst': round(igst, 2),
            'total_tax': round(total_tax, 2)
        }
    
    def _calculate_due_date(self, payment_terms):
        terms_lower = payment_terms.lower()
        
        if '30 days' in terms_lower or '30days' in terms_lower:
            days = 30
        elif '15 days' in terms_lower or '15days' in terms_lower:
            days = 15
        elif '7 days' in terms_lower or '7days' in terms_lower:
            days = 7
        elif 'immediate' in terms_lower or 'delivery' in terms_lower:
            days = 0
        else:
            days = 30
        
        due_date = datetime.now() + timedelta(days=days)
        return due_date.strftime('%Y-%m-%d')
    
    def _enhance_with_ai_insights(self, request, invoice_data):
        try:
            prompt = f"""You are an expert accounts and finance analyst. Analyze this invoice and provide professional insights.

Customer: {request['customer_name']}
Product: {request['product_description']}
Quantity: {request['quantity_delivered']} units
Invoice Amount: ₹{invoice_data['grand_total']}
Balance Due: ₹{invoice_data['balance_due']}
Payment Terms: {request['payment_terms']}

Quality Status: {request['quality_decision']}
Delivery: {request['delivery_date']}

Provide JSON response:
{{
  "payment_risk_assessment": "LOW/MEDIUM/HIGH - Brief assessment of payment risk",
  "collection_priority": "HIGH/MEDIUM/LOW",
  "recommended_actions": ["action 1", "action 2"],
  "customer_relationship_notes": "Brief note on customer relationship",
  "financial_health_indicator": "HEALTHY/WATCH/CONCERN"
}}

Be specific and business-focused."""
            
            ai_response = self.gemini.generate_json(prompt, temperature=0.3)
            return ai_response
        
        except Exception as e:
            return {
                'payment_risk_assessment': f'AI analysis unavailable: {str(e)}',
                'collection_priority': 'MEDIUM',
                'recommended_actions': ['Follow standard collection process'],
                'customer_relationship_notes': 'Standard customer',
                'financial_health_indicator': 'HEALTHY'
            }
    
    def _generate_invoice_number(self):
        return f"INV-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
    
    def generate_report(self, invoice_result):
        """Generate formatted markdown report for invoice."""
        lines = []
        lines.append("# 📄 TAX INVOICE")
        lines.append(f"\n**Invoice Number:** {invoice_result['invoice_number']}")
        lines.append(f"**Invoice Date:** {invoice_result['invoice_date']}")
        lines.append(f"**Due Date:** {invoice_result['due_date']}\n")
        
        lines.append("---\n")
        
        lines.append("## 🏢 Supplier Details")
        comp = invoice_result['company_details']
        lines.append(f"**{comp['name']}**")
        lines.append(f"{comp['address']}")
        lines.append(f"GSTIN: {comp['gstin']}")
        lines.append(f"PAN: {comp['pan']}")
        lines.append(f"Contact: {comp['contact']}\n")
        
        lines.append("## 👤 Customer Details")
        cust = invoice_result['customer_details']
        lines.append(f"**{cust['name']}**")
        lines.append(f"{cust['address']}")
        lines.append(f"GSTIN: {cust['gstin']}")
        lines.append(f"State: {cust['state']} ({cust['state_code']})\n")
        
        lines.append("## 📋 Reference Documents")
        ref = invoice_result['reference_documents']
        lines.append(f"- Quote ID: {ref['quote_id']}")
        lines.append(f"- Order ID: {ref['order_id']}")
        lines.append(f"- PO Number: {ref['po_number']}")
        lines.append(f"- Batch ID: {ref['batch_id']}")
        lines.append(f"- Inspection ID: {ref['inspection_id']}\n")
        
        lines.append("## 📦 Product Details")
        prod = invoice_result['product_details']
        lines.append(f"- **Description:** {prod['description']}")
        lines.append(f"- **HSN Code:** {prod['hsn_code']}")
        lines.append(f"- **Quantity Ordered:** {prod['quantity_ordered']} units")
        lines.append(f"- **Quantity Delivered:** {prod['quantity_delivered']} units")
        lines.append(f"- **Unit Price:** ₹{prod['unit_price']}")
        lines.append(f"- **Quality Status:** {prod['quality_decision']}\n")
        
        lines.append("## 💰 Cost Breakdown")
        cost = invoice_result['cost_breakdown']
        lines.append(f"- Material Cost: ₹{cost['material_cost']}")
        lines.append(f"- Production Cost: ₹{cost['production_cost']}")
        lines.append(f"- Quality Cost: ₹{cost['quality_cost']}")
        lines.append(f"- Packaging Cost: ₹{cost['packaging_cost']}")
        lines.append(f"- **Subtotal: ₹{cost['subtotal']}**\n")
        
        lines.append("## 🔧 Adjustments")
        adj = invoice_result['adjustments']
        if adj['discount'] > 0:
            lines.append(f"- Discount: -₹{adj['discount']}")
        if adj['additional_charges'] > 0:
            lines.append(f"- Additional Charges: +₹{adj['additional_charges']}")
        if adj['quality_bonus'] != 0:
            lines.append(f"- Quality Bonus: ₹{adj['quality_bonus']}")
        lines.append(f"- **Adjusted Amount: ₹{invoice_result['adjusted_amount']}**\n")
        
        lines.append("## 💵 Tax Details")
        tax = invoice_result['tax_details']
        lines.append(f"- Tax Type: {tax['tax_type']}")
        lines.append(f"- GST Rate: {tax['gst_rate']}%")
        if tax['tax_type'] == 'IGST':
            lines.append(f"- IGST: ₹{tax['igst']}")
        else:
            lines.append(f"- CGST: ₹{tax['cgst']}")
            lines.append(f"- SGST: ₹{tax['sgst']}")
        lines.append(f"- **Total Tax: ₹{tax['total_tax']}**\n")
        
        lines.append("## 📊 Invoice Summary")
        lines.append(f"- **Subtotal:** ₹{invoice_result['cost_breakdown']['subtotal']}")
        lines.append(f"- **Adjustments:** ₹{invoice_result['adjustments']['total']}")
        lines.append(f"- **Taxable Amount:** ₹{invoice_result['adjusted_amount']}")
        lines.append(f"- **Total Tax:** ₹{invoice_result['tax_details']['total_tax']}")
        lines.append(f"- **GRAND TOTAL:** ₹{invoice_result['grand_total']}\n")
        
        lines.append("## 💳 Payment Details")
        pay = invoice_result['payment_details']
        lines.append(f"- **Advance Paid:** ₹{pay['advance_paid']}")
        lines.append(f"- **BALANCE DUE:** ₹{pay['balance_due']}")
        lines.append(f"- **Payment Terms:** {pay['payment_terms']}")
        lines.append(f"- **Due Date:** {pay['due_date']}\n")
        
        lines.append("## 🏦 Bank Details")
        bank = invoice_result['bank_details']
        lines.append(f"- Bank Name: {bank['bank_name']}")
        lines.append(f"- Account Number: {bank['account_number']}")
        lines.append(f"- IFSC Code: {bank['ifsc_code']}")
        lines.append(f"- Branch: {bank['branch']}\n")
        
        lines.append("## 🚚 Delivery Details")
        deliv = invoice_result['delivery_details']
        lines.append(f"- Delivery Date: {deliv['delivery_date']}")
        lines.append(f"- Delivery Challan: {deliv['delivery_challan']}")
        lines.append(f"- Transport: {deliv['transport_details']}\n")
        
        ai = invoice_result['ai_insights']
        if ai.get('payment_risk_assessment'):
            lines.append("## 🤖 AI Insights")
            lines.append(f"- **Payment Risk:** {ai['payment_risk_assessment']}")
            lines.append(f"- **Collection Priority:** {ai.get('collection_priority', 'N/A')}")
            lines.append(f"- **Financial Health:** {ai.get('financial_health_indicator', 'N/A')}")
            if ai.get('recommended_actions'):
                lines.append(f"- **Actions:** {'; '.join(ai['recommended_actions'])}")
        
        lines.append("\n---")
        lines.append("\n*This is a computer-generated invoice and does not require a signature.*")
        
        return "\n".join(lines)
