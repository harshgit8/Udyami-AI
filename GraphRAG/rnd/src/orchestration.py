from typing import Dict, List, Any, Optional
from .rd_agent_core import RDAgent

class AgentOrchestrator:
    def __init__(self, rd_agent: Optional[RDAgent] = None):
        self.rd_agent = rd_agent or RDAgent()
        self.agents = {'rd': self.rd_agent}
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        rd_result = self.rd_agent.design_formulation(request)
        
        enhanced_result = {
            'technical_analysis': rd_result,
            'commercial_summary': self._generate_commercial_summary(rd_result, request),
            'production_plan': self._generate_production_plan(rd_result, request),
            'executive_summary': self._generate_executive_summary(rd_result, request)
        }
        
        return enhanced_result
    
    def _generate_commercial_summary(self, rd_result: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        if not rd_result.get('recommendations'):
            return {'error': 'No recommendations available'}
        
        best = rd_result['recommendations'][0]
        cost = best.get('cost_analysis', {}).get('total_cost_per_kg', 0)
        volume = request.get('volume_kg', 100)
        
        return {
            'unit_cost': f"₹{cost}/kg",
            'total_batch_cost': f"₹{cost * volume:,.0f}",
            'margin_analysis': {
                'material_cost': f"{cost * 0.85:.1f}",
                'processing_cost': f"{cost * 0.10:.1f}",
                'overhead': f"{cost * 0.05:.1f}"
            },
            'pricing_recommendation': f"₹{cost * 1.25:.1f}/kg (25% margin)"
        }
    
    def _generate_production_plan(self, rd_result: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        volume = request.get('volume_kg', 100)
        
        return {
            'batch_size': f"{volume}kg",
            'production_time': f"{max(4, volume/200):.1f} hours",
            'equipment_required': ['High-speed mixer', 'Twin-screw extruder'],
            'quality_checkpoints': ['Raw material inspection', 'In-process monitoring', 'Final testing'],
            'timeline': {
                'material_procurement': '2-3 days',
                'production': '1 day',
                'quality_testing': '1 day',
                'total_lead_time': '4-5 days'
            }
        }
    
    def _generate_executive_summary(self, rd_result: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        if not rd_result.get('recommendations'):
            return {'status': 'No viable formulations found'}
        
        best = rd_result['recommendations'][0]
        
        return {
            'recommendation': best.get('name', 'Unknown'),
            'cost_per_kg': f"₹{best.get('cost_analysis', {}).get('total_cost_per_kg', 0)}",
            'compliance_status': best.get('compliance', {}).get('verdict', 'Unknown'),
            'success_probability': best.get('risk', {}).get('success_probability', 'Unknown'),
            'key_benefits': [
                f"Cost-optimized formulation within ₹{request.get('cost_limit', 70)}/kg budget",
                f"Meets {request.get('quality_target', 'quality')} standards",
                f"Ready for production in {request.get('delivery_days', 10)} days"
            ]
        }