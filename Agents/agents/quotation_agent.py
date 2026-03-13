import json
from datetime import datetime, timedelta

class QuotationAgent:
    def __init__(self, gemini_client):
        self.gemini = gemini_client
        self.pricing_config = self._init_pricing_config()
        self.machine_rates = self._init_machine_rates()
        self.material_costs = self._init_material_costs()
    
    def generate_quotation(self, quote_request):
        """
        Generate comprehensive quotation based on multi-agent data.
        
        Args:
            quote_request (dict): {
                'quote_request_id': str,
                'customer': str,
                'product_type': str,
                'quantity': int,
                'application': str,
                'quality_standard': str,
                'priority': str,
                'delivery_required': str,
                'special_requirements': str,
                'material_formulation': str,
                'material_cost_per_kg': float,
                'weight_per_unit_kg': float,
                'ul94_rating': str,
                'compliance': str,
                'machine': str,
                'production_rate': float,
                'setup_time_hours': float,
                'inspection_standard': str,
                'quality_level': str,
                'risk_level': str
            }
        
        Returns:
            dict: Complete quotation with breakdown
        """
        material_cost = self._calculate_material_cost(quote_request)
        production_cost = self._calculate_production_cost(quote_request)
        quality_cost = self._calculate_quality_cost(quote_request)
        risk_premium = self._calculate_risk_premium(quote_request, material_cost, production_cost)
        
        subtotal = material_cost['total'] + production_cost['total'] + quality_cost['total'] + risk_premium['total']
        
        profit_margin = self._calculate_profit_margin(quote_request, subtotal)
        packaging_cost = self._calculate_packaging_cost(quote_request)
        documentation_cost = self._calculate_documentation_cost(quote_request)
        
        total_before_tax = subtotal + profit_margin['amount'] + packaging_cost + documentation_cost
        gst = total_before_tax * 0.18
        grand_total = total_before_tax + gst
        
        unit_price = grand_total / quote_request['quantity']
        lead_time_days = self._calculate_lead_time(quote_request)
        
        ai_enhanced = self._enhance_with_ai_insights(quote_request, {
            'material_cost': material_cost,
            'production_cost': production_cost,
            'quality_cost': quality_cost,
            'risk_premium': risk_premium,
            'grand_total': grand_total,
            'unit_price': unit_price
        })
        
        return {
            'quote_id': self._generate_quote_id(),
            'timestamp': datetime.now().isoformat(),
            'quote_request_id': quote_request['quote_request_id'],
            'customer': quote_request['customer'],
            'product_type': quote_request['product_type'],
            'quantity': quote_request['quantity'],
            'material_cost': material_cost,
            'production_cost': production_cost,
            'quality_cost': quality_cost,
            'risk_premium': risk_premium,
            'subtotal': subtotal,
            'profit_margin': profit_margin,
            'packaging_cost': packaging_cost,
            'documentation_cost': documentation_cost,
            'total_before_tax': total_before_tax,
            'gst': gst,
            'grand_total': grand_total,
            'unit_price': unit_price,
            'lead_time_days': lead_time_days,
            'valid_until': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'payment_terms': '50% advance, 50% on delivery',
            'ai_insights': ai_enhanced
        }
    
    def _init_pricing_config(self):
        return {
            'waste_factor': 0.08,
            'overhead_percent': 0.20,
            'gst_percent': 0.18,
            'profit_margin_standard': 0.25,
            'profit_margin_high_priority': 0.35,
            'profit_margin_critical': 0.40,
            'rush_premium': 0.25,
            'complex_formulation_premium': 0.10,
            'material_shortage_premium': 0.15
        }
    
    def _init_machine_rates(self):
        return {
            'M1': {'rate_per_hour': 500, 'labor_rate': 200},
            'M2': {'rate_per_hour': 600, 'labor_rate': 200},
            'M3': {'rate_per_hour': 550, 'labor_rate': 200}
        }
    
    def _init_material_costs(self):
        return {
            'steel': 80,
            'plastic': 120,
            'aluminum': 200,
            'copper': 450,
            'pvc_k67': 85,
            'pvc_k70': 78,
            'pp_homopolymer': 95,
            'ldpe': 65
        }
    
    def _calculate_material_cost(self, request):
        quantity = request['quantity']
        weight_per_unit = request.get('weight_per_unit_kg', 0.5)
        cost_per_kg = request.get('material_cost_per_kg', 80)
        
        raw_material = quantity * weight_per_unit * cost_per_kg
        waste = raw_material * self.pricing_config['waste_factor']
        total = raw_material + waste
        
        return {
            'raw_material': round(raw_material, 2),
            'waste': round(waste, 2),
            'waste_percent': self.pricing_config['waste_factor'] * 100,
            'total': round(total, 2)
        }
    
    def _calculate_production_cost(self, request):
        quantity = request['quantity']
        production_rate = request.get('production_rate', 10)
        setup_time = request.get('setup_time_hours', 1.5)
        machine = request.get('machine', 'M1')
        
        machine_config = self.machine_rates.get(machine, self.machine_rates['M1'])
        
        production_hours = quantity / production_rate
        total_hours = production_hours + setup_time
        
        machine_cost = total_hours * machine_config['rate_per_hour']
        labor_cost = total_hours * machine_config['labor_rate']
        overhead = (machine_cost + labor_cost) * self.pricing_config['overhead_percent']
        
        total = machine_cost + labor_cost + overhead
        
        return {
            'production_hours': round(production_hours, 2),
            'setup_hours': setup_time,
            'total_hours': round(total_hours, 2),
            'machine_cost': round(machine_cost, 2),
            'labor_cost': round(labor_cost, 2),
            'overhead': round(overhead, 2),
            'overhead_percent': self.pricing_config['overhead_percent'] * 100,
            'total': round(total, 2)
        }
    
    def _calculate_quality_cost(self, request):
        inspection_standard = request.get('inspection_standard', 'ISO_2859')
        quality_level = request.get('quality_level', 'GOOD')
        special_requirements = request.get('special_requirements', '')
        
        inspection_cost_map = {
            'ISO_2859': 1000,
            'ASTM_D2562': 1500,
            'ISO_9001': 2000,
            'ISO_3951': 1200
        }
        
        inspection_cost = inspection_cost_map.get(inspection_standard, 1000)
        
        testing_cost = 0
        if 'UL94' in special_requirements or 'certification' in special_requirements.lower():
            testing_cost = 3000
        elif 'testing' in special_requirements.lower():
            testing_cost = 1500
        
        certification_cost = 0
        if 'UL' in special_requirements or 'ISO' in special_requirements:
            certification_cost = 5000
        
        total = inspection_cost + testing_cost + certification_cost
        
        return {
            'inspection_cost': inspection_cost,
            'testing_cost': testing_cost,
            'certification_cost': certification_cost,
            'total': round(total, 2)
        }
    
    def _calculate_risk_premium(self, request, material_cost, production_cost):
        priority = request.get('priority', 'normal').lower()
        ul94_rating = request.get('ul94_rating', 'HB')
        risk_level = request.get('quality_level', 'Low')
        
        base_cost = material_cost['total'] + production_cost['total']
        
        priority_premium = 0
        if priority == 'critical':
            priority_premium = base_cost * 0.25
        elif priority == 'high':
            priority_premium = base_cost * 0.15
        
        formulation_premium = 0
        if ul94_rating == 'V-0':
            formulation_premium = base_cost * 0.10
        elif ul94_rating == 'V-1':
            formulation_premium = base_cost * 0.05
        
        quality_risk_premium = 0
        if 'High' in risk_level or 'Critical' in risk_level:
            quality_risk_premium = base_cost * 0.10
        elif 'Medium' in risk_level:
            quality_risk_premium = base_cost * 0.05
        
        total = priority_premium + formulation_premium + quality_risk_premium
        
        return {
            'priority_premium': round(priority_premium, 2),
            'formulation_premium': round(formulation_premium, 2),
            'quality_risk_premium': round(quality_risk_premium, 2),
            'total': round(total, 2)
        }
    
    def _calculate_profit_margin(self, request, subtotal):
        priority = request.get('priority', 'normal').lower()
        
        if priority == 'critical':
            margin_percent = self.pricing_config['profit_margin_critical']
        elif priority == 'high':
            margin_percent = self.pricing_config['profit_margin_high_priority']
        else:
            margin_percent = self.pricing_config['profit_margin_standard']
        
        amount = subtotal * margin_percent
        
        return {
            'percent': margin_percent * 100,
            'amount': round(amount, 2)
        }
    
    def _calculate_packaging_cost(self, request):
        quantity = request['quantity']
        product_type = request.get('product_type', '')
        
        cost_per_unit = 100
        if 'widget_c' in product_type:
            cost_per_unit = 150
        elif 'widget_b' in product_type:
            cost_per_unit = 120
        
        return round(quantity * cost_per_unit, 2)
    
    def _calculate_documentation_cost(self, request):
        special_requirements = request.get('special_requirements', '')
        
        base_cost = 500
        
        if 'certification' in special_requirements.lower():
            base_cost += 1500
        if 'compliance' in special_requirements.lower():
            base_cost += 500
        
        return base_cost
    
    def _calculate_lead_time(self, request):
        quantity = request['quantity']
        production_rate = request.get('production_rate', 10)
        priority = request.get('priority', 'normal').lower()
        
        production_days = (quantity / production_rate) / 8
        
        setup_days = 1
        quality_days = 2
        buffer_days = 3
        
        if priority == 'critical':
            buffer_days = 1
        elif priority == 'high':
            buffer_days = 2
        
        total_days = production_days + setup_days + quality_days + buffer_days
        
        return round(total_days)
    
    def _enhance_with_ai_insights(self, request, cost_breakdown):
        try:
            prompt = f"""You are an expert pricing and quotation analyst. Analyze this quotation and provide professional insights.

Customer: {request['customer']}
Product: {request['product_type']}
Quantity: {request['quantity']}
Priority: {request.get('priority', 'normal')}
Application: {request.get('application', 'N/A')}

Cost Breakdown:
- Material Cost: ₹{cost_breakdown['material_cost']['total']}
- Production Cost: ₹{cost_breakdown['production_cost']['total']}
- Quality Cost: ₹{cost_breakdown['quality_cost']['total']}
- Risk Premium: ₹{cost_breakdown['risk_premium']['total']}
- Grand Total: ₹{cost_breakdown['grand_total']}
- Unit Price: ₹{cost_breakdown['unit_price']}

Provide JSON response:
{{
  "pricing_analysis": "Brief analysis of pricing competitiveness (2-3 sentences)",
  "cost_optimization_opportunities": ["opportunity 1", "opportunity 2"],
  "value_proposition": "Key value points to highlight to customer",
  "negotiation_flexibility": "LOW/MEDIUM/HIGH",
  "win_probability": "HIGH/MEDIUM/LOW",
  "recommendations": "Strategic recommendation for sales team"
}}

Be specific and business-focused."""
            
            ai_response = self.gemini.generate_json(prompt, temperature=0.3)
            return ai_response
        
        except Exception as e:
            return {
                'pricing_analysis': f'AI analysis unavailable: {str(e)}',
                'cost_optimization_opportunities': [],
                'value_proposition': 'Quality product with competitive pricing',
                'negotiation_flexibility': 'MEDIUM',
                'win_probability': 'MEDIUM',
                'recommendations': 'Standard quotation process'
            }
    
    def _generate_quote_id(self):
        return f"QT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def generate_report(self, quotation_result):
        """Generate formatted markdown report for quotation."""
        lines = []
        lines.append("# 💰 QUOTATION")
        lines.append(f"\n**Quote ID:** {quotation_result['quote_id']}")
        lines.append(f"**Date:** {quotation_result['timestamp'][:10]}")
        lines.append(f"**Valid Until:** {quotation_result['valid_until']}\n")
        
        lines.append("## 📋 Customer Information")
        lines.append(f"- **Customer:** {quotation_result['customer']}")
        lines.append(f"- **Request ID:** {quotation_result['quote_request_id']}")
        lines.append(f"- **Product:** {quotation_result['product_type']}")
        lines.append(f"- **Quantity:** {quotation_result['quantity']} units\n")
        
        lines.append("## 💵 Cost Breakdown")
        
        lines.append("\n### 1. Material Cost")
        mat = quotation_result['material_cost']
        lines.append(f"- Raw Material: ₹{mat['raw_material']}")
        lines.append(f"- Waste ({mat['waste_percent']}%): ₹{mat['waste']}")
        lines.append(f"- **Total Material: ₹{mat['total']}**\n")
        
        lines.append("### 2. Production Cost")
        prod = quotation_result['production_cost']
        lines.append(f"- Production Hours: {prod['production_hours']}")
        lines.append(f"- Setup Hours: {prod['setup_hours']}")
        lines.append(f"- Machine Cost: ₹{prod['machine_cost']}")
        lines.append(f"- Labor Cost: ₹{prod['labor_cost']}")
        lines.append(f"- Overhead ({prod['overhead_percent']}%): ₹{prod['overhead']}")
        lines.append(f"- **Total Production: ₹{prod['total']}**\n")
        
        lines.append("### 3. Quality Assurance Cost")
        qual = quotation_result['quality_cost']
        lines.append(f"- Inspection: ₹{qual['inspection_cost']}")
        lines.append(f"- Testing: ₹{qual['testing_cost']}")
        lines.append(f"- Certification: ₹{qual['certification_cost']}")
        lines.append(f"- **Total Quality: ₹{qual['total']}**\n")
        
        lines.append("### 4. Risk Premium")
        risk = quotation_result['risk_premium']
        lines.append(f"- Priority Premium: ₹{risk['priority_premium']}")
        lines.append(f"- Formulation Premium: ₹{risk['formulation_premium']}")
        lines.append(f"- Quality Risk: ₹{risk['quality_risk_premium']}")
        lines.append(f"- **Total Risk Premium: ₹{risk['total']}**\n")
        
        lines.append("### 5. Additional Costs")
        lines.append(f"- Packaging: ₹{quotation_result['packaging_cost']}")
        lines.append(f"- Documentation: ₹{quotation_result['documentation_cost']}\n")
        
        lines.append("## 📊 Summary")
        lines.append(f"- **Subtotal:** ₹{quotation_result['subtotal']}")
        profit = quotation_result['profit_margin']
        lines.append(f"- **Profit Margin ({profit['percent']}%):** ₹{profit['amount']}")
        lines.append(f"- **Total Before Tax:** ₹{quotation_result['total_before_tax']}")
        lines.append(f"- **GST (18%):** ₹{quotation_result['gst']}")
        lines.append(f"- **GRAND TOTAL:** ₹{quotation_result['grand_total']}\n")
        
        lines.append("## 💎 Pricing")
        lines.append(f"- **Unit Price:** ₹{round(quotation_result['unit_price'], 2)} per unit")
        lines.append(f"- **Lead Time:** {quotation_result['lead_time_days']} days")
        lines.append(f"- **Payment Terms:** {quotation_result['payment_terms']}\n")
        
        ai = quotation_result['ai_insights']
        if ai.get('pricing_analysis'):
            lines.append("## 🤖 AI Insights")
            lines.append(f"- **Analysis:** {ai['pricing_analysis']}")
            lines.append(f"- **Value Proposition:** {ai.get('value_proposition', 'N/A')}")
            lines.append(f"- **Win Probability:** {ai.get('win_probability', 'N/A')}")
            lines.append(f"- **Negotiation Flexibility:** {ai.get('negotiation_flexibility', 'N/A')}")
        
        return "\n".join(lines)
