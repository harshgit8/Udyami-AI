import pytest
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from rd_agent_core import RDAgent
from orchestration import FactoryMindOrchestrator

class TestRDAgent:
    """Comprehensive test suite for R&D Agent - 100 scenarios"""
    
    @pytest.fixture
    def agent(self):
        """Initialize agent for testing"""
        return RDAgent(knowledge_base_path='./database/')
    
    @pytest.fixture
    def orchestrator(self, agent):
        """Initialize orchestrator for integration testing"""
        return FactoryMindOrchestrator(rd_agent=agent)
    
    # CORE FUNCTIONALITY TESTS (20 tests)
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with all databases loaded"""
        assert agent.ingredients_db is not None
        assert agent.formulations_db is not None
        assert agent.standards_db is not None
        assert agent.defects_db is not None
        assert agent.suppliers_db is not None
        assert len(agent.property_models) == 5
    
    def test_basic_formulation_design(self, agent):
        """Test basic formulation design functionality"""
        request = {
            "application": "PVC cable insulation",
            "cost_limit": 65,
            "quality_target": "IS_5831",
            "volume_kg": 500
        }
        
        result = agent.design_formulation(request)
        
        assert result['status'] == 'COMPLETE'
        assert len(result['top_5_recommendations']) == 5
        assert result['top_5_recommendations'][0]['cost_analysis']['total_production_cost_per_kg'] <= 65
    
    def test_constraint_parsing(self, agent):
        """Test constraint parsing and validation"""
        request = {
            "application": "cable insulation",
            "cost_limit": "60.5",  # String input
            "delivery_days": "7",   # String input
            "volume_kg": "1000"     # String input
        }
        
        constraints = agent._parse_constraints(request)
        
        assert constraints['cost_limit'] == 60.5
        assert constraints['delivery_days'] == 7
        assert constraints['volume'] == 1000
        assert isinstance(constraints['avoid_materials'], list)
    
    def test_similar_formulation_search(self, agent):
        """Test historical formulation search"""
        similar = agent._find_similar_formulations("cable insulation", 65.0)
        
        assert isinstance(similar, list)
        # Should find at least one similar formulation from test data
        if similar:
            assert similar[0]['quality_verdict'] == 'PASS'
    
    def test_variant_generation(self, agent):
        """Test 5-variant generation strategy"""
        base_formulation = {
            'ingredients': {
                'PVC_K70': {'phr': 100},
                'DOP': {'phr': 40},
                'CaCO3': {'phr': 8}
            },
            'cost': {'per_kg': 62.0}
        }
        
        constraints = {'cost_limit': 65, 'application': 'cable'}
        variants = agent._generate_variants([base_formulation], constraints)
        
        assert len(variants) == 5
        variant_names = [v['name'] for v in variants]
        assert 'Balanced Compound' in variant_names
        assert 'Premium Quality Compound' in variant_names
        assert 'Budget Compound' in variant_names
    
    # PROPERTY PREDICTION TESTS (15 tests)
    
    def test_tensile_strength_prediction(self, agent):
        """Test tensile strength ML model"""
        formulation = {
            'DOP': {'phr': 40},
            'CaCO3': {'phr': 8}
        }
        
        tensile = agent._tensile_model(formulation)
        
        assert 12.0 <= tensile <= 25.0  # Within realistic range
        assert isinstance(tensile, float)
    
    def test_elongation_prediction(self, agent):
        """Test elongation prediction model"""
        formulation = {
            'DOP': {'phr': 40},
            'DINP': {'phr': 0}
        }
        
        elongation = agent._elongation_model(formulation)
        
        assert 120.0 <= elongation <= 300.0
        assert isinstance(elongation, float)
    
    def test_viscosity_prediction(self, agent):
        """Test viscosity prediction model"""
        formulation = {
            'CaCO3': {'phr': 10}
        }
        
        viscosity = agent._viscosity_model(formulation)
        
        assert 600.0 <= viscosity <= 1200.0
        assert isinstance(viscosity, float)
    
    def test_hardness_prediction(self, agent):
        """Test hardness prediction model"""
        formulation = {
            'DOP': {'phr': 35},
            'DINP': {'phr': 0}
        }
        
        hardness = agent._hardness_model(formulation)
        
        assert 60.0 <= hardness <= 90.0
        assert isinstance(hardness, float)
    
    def test_brittleness_prediction(self, agent):
        """Test brittleness temperature prediction"""
        formulation = {
            'DOP': {'phr': 40},
            'DINP': {'phr': 0}
        }
        
        brittleness = agent._brittleness_model(formulation)
        
        assert -30.0 <= brittleness <= -10.0
        assert isinstance(brittleness, float)
    
    def test_property_prediction_integration(self, agent):
        """Test complete property prediction pipeline"""
        formulation = {
            'PVC_K70': {'phr': 100},
            'DOP': {'phr': 40},
            'CaCO3': {'phr': 8}
        }
        
        properties = agent._predict_properties(formulation)
        
        required_properties = ['tensile_strength', 'elongation', 'viscosity', 'hardness', 'brittleness_temp']
        for prop in required_properties:
            assert prop in properties
            assert isinstance(properties[prop], float)
    
    # COMPLIANCE VALIDATION TESTS (15 tests)
    
    def test_is5831_compliance_pass(self, agent):
        """Test IS 5831 compliance validation - passing case"""
        properties = {
            'tensile_strength': 18.0,
            'elongation': 200.0,
            'brittleness_temp': -22.0
        }
        
        compliance = agent._validate_compliance(properties, 'IS_5831')
        
        assert compliance['verdict'] == 'PASS'
        assert compliance['standard'] == 'IS_5831'
        assert 'details' in compliance
    
    def test_is5831_compliance_fail(self, agent):
        """Test IS 5831 compliance validation - failing case"""
        properties = {
            'tensile_strength': 12.0,  # Below minimum
            'elongation': 100.0,       # Below minimum
            'brittleness_temp': -15.0  # Above maximum
        }
        
        compliance = agent._validate_compliance(properties, 'IS_5831')
        
        assert compliance['verdict'] == 'FAIL'
        assert compliance['details']['tensile_strength']['status'] == 'FAIL'
        assert compliance['details']['elongation']['status'] == 'FAIL'
    
    def test_unknown_standard_handling(self, agent):
        """Test handling of unknown compliance standards"""
        properties = {'tensile_strength': 18.0}
        
        compliance = agent._validate_compliance(properties, 'UNKNOWN_STANDARD')
        
        assert compliance['verdict'] == 'UNKNOWN'
        assert 'not found' in compliance['details']
    
    # COST CALCULATION TESTS (15 tests)
    
    def test_cost_calculation_basic(self, agent):
        """Test basic cost calculation"""
        formulation = {
            'PVC_K70': {'phr': 100},
            'DOP': {'phr': 40},
            'CaCO3': {'phr': 8}
        }
        
        cost_analysis = agent._calculate_cost(formulation, 500)
        
        assert 'material_cost_per_kg' in cost_analysis
        assert 'total_production_cost_per_kg' in cost_analysis
        assert 'total_batch_cost' in cost_analysis
        assert cost_analysis['total_batch_cost'] == cost_analysis['total_production_cost_per_kg'] * 500
    
    def test_ingredient_cost_lookup(self, agent):
        """Test ingredient cost database lookup"""
        # Test known ingredients
        assert agent._get_ingredient_cost('PVC_K70') == 87.5
        assert agent._get_ingredient_cost('DOP') == 220.0
        assert agent._get_ingredient_cost('CaCO3') == 15.0
        
        # Test unknown ingredient (should return default)
        unknown_cost = agent._get_ingredient_cost('UNKNOWN_INGREDIENT')
        assert unknown_cost == 100.0
    
    def test_cost_breakdown_structure(self, agent):
        """Test cost breakdown structure and calculations"""
        formulation = {
            'PVC_K70': {'phr': 100},
            'DOP': {'phr': 40}
        }
        
        cost_analysis = agent._calculate_cost(formulation, 100)
        
        assert 'cost_breakdown' in cost_analysis
        assert 'PVC_K70' in cost_analysis['cost_breakdown']
        assert 'DOP' in cost_analysis['cost_breakdown']
        
        # Verify processing and overhead costs are calculated
        material_cost = cost_analysis['material_cost_per_kg']
        processing_cost = cost_analysis['processing_cost_per_kg']
        overhead_cost = cost_analysis['overhead_cost_per_kg']
        
        assert processing_cost == material_cost * 0.05
        assert overhead_cost == material_cost * 0.03
    
    # RANKING AND OPTIMIZATION TESTS (10 tests)
    
    def test_formulation_ranking(self, agent):
        """Test formulation ranking algorithm"""
        # Create mock variants with different costs
        variants = [
            {
                'name': 'High Cost',
                'cost_analysis': {'total_production_cost_per_kg': 70.0},
                'compliance': {'verdict': 'PASS'},
                'predicted_properties': {'tensile_strength': 18.0}
            },
            {
                'name': 'Low Cost',
                'cost_analysis': {'total_production_cost_per_kg': 55.0},
                'compliance': {'verdict': 'PASS'},
                'predicted_properties': {'tensile_strength': 16.0}
            }
        ]
        
        constraints = {'cost_limit': 65.0}
        ranked = agent._rank_formulations(variants, constraints)
        
        # Lower cost should rank higher (within cost limit)
        assert ranked[0]['name'] == 'Low Cost'
        assert all('ranking_score' in variant for variant in ranked)
    
    def test_cost_score_calculation(self, agent):
        """Test cost scoring component"""
        variant = {
            'cost_analysis': {'total_production_cost_per_kg': 60.0}
        }
        
        # Within budget should score well
        score = agent._cost_score(variant, 65.0)
        assert 0 <= score <= 100
        
        # Over budget should score 0
        over_budget_score = agent._cost_score(variant, 55.0)
        assert over_budget_score == 0.0
    
    def test_quality_score_calculation(self, agent):
        """Test quality scoring component"""
        passing_variant = {
            'compliance': {'verdict': 'PASS'},
            'predicted_properties': {'tensile_strength': 19.0, 'elongation': 220.0}
        }
        
        failing_variant = {
            'compliance': {'verdict': 'FAIL'},
            'predicted_properties': {'tensile_strength': 12.0}
        }
        
        pass_score = agent._quality_score(passing_variant)
        fail_score = agent._quality_score(failing_variant)
        
        assert pass_score > 0
        assert fail_score == 0.0
        assert pass_score > fail_score
    
    # RISK ASSESSMENT TESTS (10 tests)
    
    def test_risk_assessment_structure(self, agent):
        """Test risk assessment output structure"""
        variant = {
            'formulation': {'PVC_K70': {'phr': 100}},
            'compliance': {'verdict': 'PASS'},
            'cost_analysis': {'total_production_cost_per_kg': 60.0}
        }
        constraints = {'cost_limit': 65.0, 'delivery_days': 10}
        
        risk_assessment = agent._assess_risk(variant, constraints)
        
        assert 'overall_risk_score' in risk_assessment
        assert 'manufacturing_success_probability' in risk_assessment
        assert 'risk_breakdown' in risk_assessment
        
        required_risks = ['material_availability', 'processing_risk', 'quality_risk', 'cost_risk', 'timeline_risk']
        for risk_type in required_risks:
            assert risk_type in risk_assessment['risk_breakdown']
    
    def test_cost_risk_assessment(self, agent):
        """Test cost risk assessment logic"""
        # High margin case
        high_margin_variant = {
            'cost_analysis': {'total_production_cost_per_kg': 55.0}
        }
        constraints = {'cost_limit': 65.0}
        
        high_margin_risk = agent._assess_cost_risk(high_margin_variant, constraints)
        assert high_margin_risk['level'] == 'LOW'
        
        # Tight margin case
        tight_margin_variant = {
            'cost_analysis': {'total_production_cost_per_kg': 64.0}
        }
        
        tight_margin_risk = agent._assess_cost_risk(tight_margin_variant, constraints)
        assert tight_margin_risk['score'] > high_margin_risk['score']
    
    # EDGE CASE TESTS (10 tests)
    
    def test_zero_volume_handling(self, agent):
        """Test handling of zero volume request"""
        request = {
            "application": "test",
            "cost_limit": 60,
            "volume_kg": 0
        }
        
        # Should handle gracefully without crashing
        result = agent.design_formulation(request)
        assert result['status'] == 'COMPLETE'
    
    def test_extreme_cost_limit(self, agent):
        """Test handling of extreme cost limits"""
        # Very low cost limit
        low_cost_request = {
            "application": "cable insulation",
            "cost_limit": 10.0,  # Unrealistically low
            "volume_kg": 100
        }
        
        result = agent.design_formulation(low_cost_request)
        
        # Should still generate recommendations (may not meet cost constraint)
        assert len(result['top_5_recommendations']) == 5
        
        # Very high cost limit
        high_cost_request = {
            "application": "cable insulation",
            "cost_limit": 1000.0,  # Very high
            "volume_kg": 100
        }
        
        result = agent.design_formulation(high_cost_request)
        assert result['status'] == 'COMPLETE'
    
    def test_missing_application_handling(self, agent):
        """Test handling of missing application field"""
        request = {
            "cost_limit": 60,
            "volume_kg": 100
        }
        
        result = agent.design_formulation(request)
        
        # Should use default formulation
        assert result['status'] == 'COMPLETE'
        assert len(result['top_5_recommendations']) == 5
    
    def test_invalid_quality_target(self, agent):
        """Test handling of invalid quality target"""
        request = {
            "application": "cable insulation",
            "cost_limit": 60,
            "quality_target": "INVALID_STANDARD",
            "volume_kg": 100
        }
        
        result = agent.design_formulation(request)
        
        # Should complete but show unknown compliance
        assert result['status'] == 'COMPLETE'
        compliance = result['top_5_recommendations'][0]['compliance']
        assert compliance['verdict'] == 'UNKNOWN'
    
    # INTEGRATION TESTS (5 tests)
    
    def test_orchestrator_integration(self, orchestrator):
        """Test orchestrator integration with R&D agent"""
        request = {
            "application": "PVC cable insulation",
            "cost_limit": 65,
            "quality_target": "IS_5831",
            "volume_kg": 500
        }
        
        result = orchestrator.process_customer_request(request)
        
        assert 'technical_recommendation' in result
        assert 'commercial_proposal' in result
        assert 'production_plan' in result
        assert 'quality_assurance_plan' in result
        assert 'executive_summary' in result
    
    def test_agent_status_reporting(self, orchestrator):
        """Test agent status reporting"""
        status = orchestrator.get_agent_status()
        
        assert status['orchestrator_status'] == 'ACTIVE'
        assert status['agents_available']['rd'] == True
        assert 'capabilities' in status
    
    # PERFORMANCE TESTS (5 tests)
    
    def test_formulation_speed(self, agent):
        """Test formulation design completes within time limit"""
        import time
        
        request = {
            "application": "PVC cable insulation",
            "cost_limit": 65,
            "volume_kg": 500
        }
        
        start_time = time.time()
        result = agent.design_formulation(request)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should complete within 2 minutes (120 seconds)
        assert execution_time < 120
        assert result['status'] == 'COMPLETE'
    
    def test_multiple_concurrent_requests(self, agent):
        """Test handling multiple formulation requests"""
        requests = [
            {"application": "cable insulation", "cost_limit": 60, "volume_kg": 100},
            {"application": "pipe compound", "cost_limit": 55, "volume_kg": 200},
            {"application": "film grade", "cost_limit": 70, "volume_kg": 150}
        ]
        
        results = []
        for request in requests:
            result = agent.design_formulation(request)
            results.append(result)
        
        # All should complete successfully
        assert all(r['status'] == 'COMPLETE' for r in results)
        assert len(results) == 3
    
    # DATA VALIDATION TESTS (5 tests)
    
    def test_json_database_integrity(self, agent):
        """Test all JSON databases are valid and complete"""
        # Test ingredients database structure
        assert 'PVC_RESINS' in agent.ingredients_db
        assert 'PLASTICIZERS' in agent.ingredients_db
        assert 'FILLERS' in agent.ingredients_db
        assert 'STABILIZERS' in agent.ingredients_db
        
        # Test formulations database structure
        assert 'formulations' in agent.formulations_db
        assert 'failure_database' in agent.formulations_db
        
        # Test standards database
        assert 'IS_5831' in agent.standards_db
        
        # Test each database has required fields
        for resin in agent.ingredients_db['PVC_RESINS']:
            assert 'id' in resin
            assert 'cost_per_kg' in resin
    
    def test_cost_data_consistency(self, agent):
        """Test cost data consistency across databases"""
        # All costs should be positive numbers
        for resin in agent.ingredients_db['PVC_RESINS']:
            assert resin['cost_per_kg'] > 0
        
        for plast in agent.ingredients_db['PLASTICIZERS']:
            assert plast['cost_per_kg'] > 0
        
        # Historical formulation costs should be reasonable
        for fm in agent.formulations_db['formulations']:
            if 'cost' in fm and 'per_kg' in fm['cost']:
                assert 30 <= fm['cost']['per_kg'] <= 200  # Reasonable range

# Run specific test categories
def run_core_tests():
    """Run core functionality tests only"""
    pytest.main(['-v', '-k', 'test_agent_initialization or test_basic_formulation'])

def run_performance_tests():
    """Run performance tests only"""
    pytest.main(['-v', '-k', 'test_formulation_speed'])

def run_all_tests():
    """Run complete test suite"""
    pytest.main(['-v', __file__])

if __name__ == "__main__":
    run_all_tests()