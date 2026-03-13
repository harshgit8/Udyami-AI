import json
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
        lines.append(f"\n**Inspection ID:** {inspection_result['inspection_id']}")
        lines.append(f"**Batch ID:** {inspection_result['batch_id']}")
        lines.append(f"**Product:** {inspection_result['product_type']}")
        lines.append(f"**Quantity:** {inspection_result['quantity']}\n")
        
        defects = inspection_result['defect_analysis']
        lines.append("## Defect Analysis")
        lines.append(f"- Total Defects: {defects['total_defects']}")
        lines.append(f"- Critical: {defects['critical_count']}")
        lines.append(f"- Major: {defects['major_count']}")
        lines.append(f"- Minor: {defects['minor_count']}")
        lines.append(f"- Defect Rate: {defects['defect_rate_percent']}%\n")
        
        sev = inspection_result['severity_assessment']
        lines.append("## Severity Assessment")
        lines.append(f"- Level: {sev['severity_level']}")
        lines.append(f"- Risk: {sev['risk_level']}\n")
        
        dec = inspection_result['final_decision']
        lines.append("## Final Decision")
        lines.append(f"**{dec['decision']}**")
        lines.append(f"- Reason: {dec['reason']}")
        lines.append(f"- Confidence: {dec['confidence']}%\n")
        
        lines.append("## Recommendation")
        lines.append(f"**{inspection_result['recommendation']}**")
        
        return "\n".join(lines)
