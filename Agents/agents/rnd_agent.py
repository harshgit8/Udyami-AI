import json
from datetime import datetime

class RnDAgent:
    def __init__(self, gemini_client):
        self.gemini = gemini_client
        self.formulation_db = {
            'pvc_v0': {'cost_per_kg': 85, 'ul94_rating': 'V-0'},
            'pvc_v1': {'cost_per_kg': 76, 'ul94_rating': 'V-1'},
            'pvc_hb': {'cost_per_kg': 58, 'ul94_rating': 'HB'}
        }
    
    def design_formulation(self, requirements):
        formulation = self._optimize_composition(requirements)
        properties = self._predict_properties(formulation)
        compliance = self._validate_compliance(formulation, requirements)
        
        return {
            'formulation_id': f"FORM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'requirements': requirements,
            'optimized_formulation': formulation,
            'predicted_properties': properties,
            'compliance': compliance,
            'recommendation': self._generate_recommendation(properties, compliance),
            'ai_insights': {}
        }
    
    def _optimize_composition(self, requirements):
        standards = requirements.get('standards', [])
        cost_target = requirements.get('cost_target', 100)
        
        target_rating = 'V-0'
        for std in standards:
            if 'V-1' in std:
                target_rating = 'V-1'
            elif 'HB' in std:
                target_rating = 'HB'
        
        if target_rating == 'V-0':
            composition = {'PVC_K67': 100, 'ATH': 45, 'Zinc_Borate': 8}
            cost = 82
        elif target_rating == 'V-1':
            composition = {'PVC_K67': 100, 'ATH': 50, 'Zinc_Borate': 6}
            cost = 76
        else:
            composition = {'PVC_K70': 100, 'Calcium_Carbonate': 15}
            cost = 58
        
        return {'composition_phr': composition, 'cost_per_kg': cost}
    
    def _predict_properties(self, formulation):
        comp = formulation['composition_phr']
        ath = comp.get('ATH', 0)
        
        if ath >= 45:
            rating = 'V-0'
            tensile = 44
        elif ath >= 40:
            rating = 'V-1'
            tensile = 42
        else:
            rating = 'HB'
            tensile = 50
        
        return {
            'ul94_rating': rating,
            'tensile_strength_mpa': tensile,
            'loi_percent': 30,
            'confidence_percent': 85
        }
    
    def _validate_compliance(self, formulation, requirements):
        return {
            'rohs': True,
            'reach': True,
            'toxicity': 'Low',
            'issues': []
        }
    
    def _generate_recommendation(self, properties, compliance):
        if properties['ul94_rating'] in ['V-0', 'V-1'] and compliance['rohs']:
            return 'PROCEED TO PILOT BATCH'
        return 'LABORATORY TESTING REQUIRED'
    
    def generate_report(self, formulation_result):
        lines = []
        lines.append("# 🧪 R&D Formulation Report")
        lines.append(f"\n**Formulation ID:** {formulation_result['formulation_id']}")
        
        req = formulation_result['requirements']
        lines.append("\n## Requirements")
        lines.append(f"- Application: {req.get('application')}")
        lines.append(f"- Standards: {', '.join(req.get('standards', []))}")
        lines.append(f"- Cost Target: ₹{req.get('cost_target')}/kg\n")
        
        form = formulation_result['optimized_formulation']
        lines.append("## Formulation")
        for mat, qty in form['composition_phr'].items():
            lines.append(f"- {mat}: {qty}")
        lines.append(f"\n**Cost:** ₹{form['cost_per_kg']}/kg\n")
        
        props = formulation_result['predicted_properties']
        lines.append("## Properties")
        lines.append(f"- UL94: {props['ul94_rating']}")
        lines.append(f"- Tensile: {props['tensile_strength_mpa']} MPa")
        lines.append(f"- Confidence: {props['confidence_percent']}%\n")
        
        lines.append("## Recommendation")
        lines.append(f"**{formulation_result['recommendation']}**")
        
        return "\n".join(lines)
