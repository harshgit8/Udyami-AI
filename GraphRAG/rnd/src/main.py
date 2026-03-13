from src.rd_agent_core import RDAgent
from src.orchestration import AgentOrchestrator
from src.llm_interface import query_formulation_agent

def main():
    print("R&D Agent System - LLM Enhanced")
    print("=" * 50)
    
    # Test LLM interface
    test_queries = [
        "I need PVC cable insulation compound for 1100V application under ₹65/kg with RoHS compliance",
        "Budget formulation for pipe compound maximum ₹50/kg meeting IS 5831 standard",
        "Export grade cable compound with REACH compliance, premium quality, cost not primary concern"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 40)
        
        try:
            result = query_formulation_agent(query)
            
            if result['status'] == 'SUCCESS':
                print(f"✓ Processing Time: {result['processing_time_seconds']}s")
                print(f"✓ Confidence: {result['confidence_score']:.2f}")
                
                for rec in result['top_3_recommendations']:
                    print(f"  {rec['rank']}. {rec['name']}: ₹{rec['cost_per_kg']}/kg ({rec['compliance']})")
            else:
                print("✗ Query failed")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ LLM-Enhanced R&D Agent Operational")

if __name__ == "__main__":
    main()