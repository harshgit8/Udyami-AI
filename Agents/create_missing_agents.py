"""Script to create missing agent files"""

# Create quality_agent.py
quality_agent_code = '''import json
from datetime import datetime

class QualityAgent:
    def __init__(self, gemini_client):
        self.gemini = gemini_client
        self.defect_types = {
            'surface_scratch': {'category': 'surface', 'severity_levels': {'minor': 1, 'moderate': 3, 'major': 5, 'critical': 10}},
            'dimensional_deviation': {'category': 'dimensional', 'severity_levels': {'minor': 2, 'moderate': 5, 'major': 8, 'critical': 10}},
            'crack': {'category': 'structural', 'severity_levels': {'minor': 5, 'moderate': 8, 'major': 10, 'critical': 10}}
        }
        self.inspection_standards = {
            'ISO_2859': {'name': 'Sampling Procedures for Inspection by Attributes', 'aql_levels': {'critical': 0.065, 'major': 1.0, 'minor': 2.5}},
            'ASTM_D2562': {'name': 'Visual Defects in Molded Parts', 'defect_classification': ['critical', 'major', 'minor']}
        }
    
    def inspect_batch(self, inspection_data):
        defect_analysis = self._analyze_defects(inspection_data)
        measurement_analysis = self._analyze_measurements(inspection_data)
        standard_compliance = self._check_standard_compliance(inspection_data, defect_analysis)
        severity_assessment = self._assess_severity(defect_analysis)
        final_decision = self._make_decision(defect_analysis, measurement_analysis, standard_compliance, severity_assessment)
        
        return {
            'inspection_id': f"QC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'batch_id': inspection_data['batch_id'],
            'product_type': inspection_data['product_type'],
            'quantity': inspection_data['quantity'],
            'defect_analysis': defect_analysis,
            'measurement_analysis': measurement_analysis,
            'standard_compliance': standard_compliance,
            'severity_assessment': severity_assessment,
            'final_decision': final_decision,
            'recommendation': self._generate_recommendation(final_decision, severity_assessment),
            'ai_insights': {}
        }
    
    def _analyze_defects(self, inspection_data):
        defects_found = inspection_data.get('defects_found', [])
        quantity = inspection_data.get('quantity', 1)
        
        defect_summary = {
            'total_defects': len(defects_found),
            'critical_count': sum(1 for d in defects_found if d.get('severity') == 'critical'),
            'major_count': sum(1 for d in defects_found if d.get('severity') == 'major'),
            'minor_count': sum(1 for d in defects_found if d.get('severity') == 'minor'),
            'defect_rate_percent': round((len(defects_found) / quantity) * 100, 2) if quantity > 0 else 0
        }
        return defect_summary
    
    def _analyze_measurements(self, inspection_data):
        measurements = inspection_data.get('measurements', {})
        return {
            'measurements_taken': len(measurements),
            'out_of_spec': [],
            'within_tolerance': list(measurements.keys())
        }
    
    def _check_standard_compliance(self, inspection_data, defect_analysis):
        return {
            'standard': inspection_data.get('inspection_standard', 'ISO_2859'),
            'compliant': defect_analysis['critical_count'] == 0,
            'violations': []
        }
    
    def _assess_severity(self, defect_analysis):
        severity_score = (defect_analysis['critical_count'] * 10 + 
                         defect_analysis['major_count'] * 5 + 
                         defect_analysis['minor_count'] * 1)
        
        if severity_score == 0:
            level = 'EXCELLENT'
        elif severity_score <= 5:
            level = 'GOOD'
        elif severity_score <= 15:
            level = 'ACCEPTABLE'
        else:
            level = 'UNACCEPTABLE'
        
        return {
            'severity_score': severity_score,
            'severity_level': level,
            'risk_level': 'Low' if severity_score <= 5 else 'Medium' if severity_score <= 15 else 'High'
        }
    
    def _make_decision(self, defect_analysis, measurement_analysis, compliance, severity):
        if defect_analysis['critical_count'] > 0:
            return {'decision': 'REJECT', 'reason': 'Critical defects found', 'confidence': 100}
        if not compliance['compliant']:
            return {'decision': 'REJECT', 'reason': 'Standard non-compliance', 'confidence': 95}
        if severity['severity_level'] in ['EXCELLENT', 'GOOD', 'ACCEPTABLE']:
            return {'decision': 'ACCEPT', 'reason': 'Quality acceptable', 'confidence': 90}
        return {'decision': 'CONDITIONAL_ACCEPT', 'reason': 'Marginal quality', 'confidence': 70}
    
    def _generate_recommendation(self, decision, severity):
        if decision['decision'] == 'REJECT':
            return 'REJECT BATCH - Do not ship'
        if decision['decision'] == 'ACCEPT' and severity['severity_level'] == 'EXCELLENT':
            return 'APPROVE FOR SHIPMENT - Excellent quality'
        if decision['decision'] == 'ACCEPT':
            return 'APPROVE FOR SHIPMENT - Quality acceptable'
        return 'CONDITIONAL APPROVAL - Review with customer'
    
    def generate_report(self, inspection_result):
        lines = []
        lines.append("# 🔍 Quality Inspection Report")
        lines.append(f"\\n**Inspection ID:** {inspection_result['inspection_id']}")
        lines.append(f"**Batch ID:** {inspection_result['batch_id']}")
        lines.append(f"**Product:** {inspection_result['product_type']}")
        lines.append(f"**Quantity:** {inspection_result['quantity']}\\n")
        
        defects = inspection_result['defect_analysis']
        lines.append("## Defect Analysis")
        lines.append(f"- Total Defects: {defects['total_defects']}")
        lines.append(f"- Critical: {defects['critical_count']}")
        lines.append(f"- Major: {defects['major_count']}")
        lines.append(f"- Minor: {defects['minor_count']}")
        lines.append(f"- Defect Rate: {defects['defect_rate_percent']}%\\n")
        
        sev = inspection_result['severity_assessment']
        lines.append("## Severity Assessment")
        lines.append(f"- Level: {sev['severity_level']}")
        lines.append(f"- Risk: {sev['risk_level']}\\n")
        
        dec = inspection_result['final_decision']
        lines.append("## Final Decision")
        lines.append(f"**{dec['decision']}**")
        lines.append(f"- Reason: {dec['reason']}")
        lines.append(f"- Confidence: {dec['confidence']}%\\n")
        
        lines.append("## Recommendation")
        lines.append(f"**{inspection_result['recommendation']}**")
        
        return "\\n".join(lines)
'''

# Create rnd_agent.py
rnd_agent_code = '''import json
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
        lines.append(f"\\n**Formulation ID:** {formulation_result['formulation_id']}")
        
        req = formulation_result['requirements']
        lines.append("\\n## Requirements")
        lines.append(f"- Application: {req.get('application')}")
        lines.append(f"- Standards: {', '.join(req.get('standards', []))}")
        lines.append(f"- Cost Target: ₹{req.get('cost_target')}/kg\\n")
        
        form = formulation_result['optimized_formulation']
        lines.append("## Formulation")
        for mat, qty in form['composition_phr'].items():
            lines.append(f"- {mat}: {qty}")
        lines.append(f"\\n**Cost:** ₹{form['cost_per_kg']}/kg\\n")
        
        props = formulation_result['predicted_properties']
        lines.append("## Properties")
        lines.append(f"- UL94: {props['ul94_rating']}")
        lines.append(f"- Tensile: {props['tensile_strength_mpa']} MPa")
        lines.append(f"- Confidence: {props['confidence_percent']}%\\n")
        
        lines.append("## Recommendation")
        lines.append(f"**{formulation_result['recommendation']}**")
        
        return "\\n".join(lines)
'''

# Write files
with open('agents/quality_agent.py', 'w', encoding='utf-8') as f:
    f.write(quality_agent_code)

with open('agents/rnd_agent.py', 'w', encoding='utf-8') as f:
    f.write(rnd_agent_code)

print("✅ Created agents/quality_agent.py")
print("✅ Created agents/rnd_agent.py")
print("\\nYou can now run:")
print("  python quality_orchestrator.py")
print("  python rnd_orchestrator.py")
