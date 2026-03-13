import json
from datetime import datetime
import config
from sheets_client import SheetsClient
from ai_client import AIClient
from agents.orders_agent import OrdersAgent
from agents.capacity_agent import CapacityAgent
from agents.materials_agent import MaterialsAgent
from agents.deadlines_agent import DeadlinesAgent
from agents.setup_agent import SetupAgent
from agents.structuring_agent import StructuringAgent
from agents.report_agent import ReportAgent
from agents.web_agent import WebAgent
from optimizer.scheduler import ProductionScheduler

class Orchestrator:
    def __init__(self):
        self.sheets_client = SheetsClient()
        self.ai_client = AIClient()
        
        self.machines_config = [
            {'machine_id': 'M1', 'capable_products': ['widget_a', 'widget_b'], 'production_rate': 10},
            {'machine_id': 'M2', 'capable_products': ['widget_b', 'widget_c'], 'production_rate': 15},
            {'machine_id': 'M3', 'capable_products': ['widget_a', 'widget_c'], 'production_rate': 12}
        ]
        
        self.materials_inventory = {
            'steel': 1000,
            'plastic': 500,
            'aluminum': 300,
            'copper': 200
        }
        
        self.setup_times = {
            'M1_widget_a': 1.5,
            'M1_widget_b': 2.0,
            'M2_widget_b': 1.0,
            'M2_widget_c': 1.5,
            'M3_widget_a': 2.0,
            'M3_widget_c': 1.0
        }
        
        self.orders_agent = OrdersAgent()
        self.capacity_agent = CapacityAgent(self.machines_config)
        self.materials_agent = MaterialsAgent(self.ai_client, self.materials_inventory)
        self.deadlines_agent = DeadlinesAgent()
        self.setup_agent = SetupAgent(self.setup_times)
        self.structuring_agent = StructuringAgent()
        self.report_agent = ReportAgent(self.ai_client)
        self.web_agent = WebAgent()
        self.scheduler = ProductionScheduler(self.machines_config)
    
    def run(self):
        print("Starting production scheduling orchestration...")
        
        print("\n[1/9] Reading orders from Google Sheets...")
        try:
            raw_rows = self.sheets_client.read_sheet("Production!A:H")
        except Exception as e:
            if "Unable to parse range" in str(e):
                print(f"  Sheet tab 'Production' not found. Trying '{config.SHEET_NAME}'...")
                raw_rows = self.sheets_client.read_sheet(f"{config.SHEET_NAME}!A:H")
            else:
                raise
        
        print("[2/9] Validating and cleaning orders...")
        orders = self.orders_agent.validate_and_clean(raw_rows)
        print(f"  Validated {len(orders)} orders")
        
        if self.orders_agent.validation_errors:
            print(f"  Validation errors: {len(self.orders_agent.validation_errors)}")
            for error in self.orders_agent.validation_errors[:5]:
                print(f"    - {error}")
        
        print("[3/9] Checking machine capacity...")
        capacity_analysis = self.capacity_agent.check_capacity(orders)
        
        print("[4/9] Checking materials availability...")
        materials_status = self.materials_agent.check_materials(orders)
        
        print("[5/9] Analyzing deadlines...")
        deadlines_analysis = self.deadlines_agent.analyze_deadlines(orders, capacity_analysis)
        
        print("[6/9] Calculating setup times...")
        setup_analysis = self.setup_agent.calculate_setup_times(orders, capacity_analysis)
        
        print("[7/9] Structuring data for optimizer...")
        structured_tasks = self.structuring_agent.structure_for_optimizer(
            orders, capacity_analysis, materials_status, 
            deadlines_analysis, setup_analysis
        )
        print(f"  Structured {len(structured_tasks)} tasks")
        
        print("[8/9] Running optimizer...")
        schedule = self.scheduler.optimize(structured_tasks)
        print(f"  Generated schedule with {len(schedule)} items")
        
        print("[9/9] Generating reports...")
        report_text, decisions = self.report_agent.generate_report(
            orders, schedule, structured_tasks
        )
        
        report_file = f"{config.REPORTS_DIR}/production_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"  Report saved: {report_file}")
        
        html_content = self.web_agent.generate_html(schedule, decisions)
        html_file = f"{config.REPORTS_DIR}/schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"  HTML schedule saved: {html_file}")
        
        self._write_decisions_to_sheet(decisions)
        
        print("\n✓ Orchestration complete!")
        return {
            'orders': orders,
            'schedule': schedule,
            'decisions': decisions,
            'report_file': report_file,
            'html_file': html_file
        }
    
    def _write_decisions_to_sheet(self, decisions):
        try:
            decision_rows = [['Order ID', 'Decision', 'Risk Score', 'Reason', 'Machine', 'Start Time', 'End Time']]
            
            for d in decisions:
                decision_rows.append([
                    d['order_id'],
                    d['decision'],
                    str(d['risk_score']),
                    d['reason'][:100],
                    d.get('machine', ''),
                    d.get('start_time', '')[:19] if d.get('start_time') else '',
                    d.get('end_time', '')[:19] if d.get('end_time') else ''
                ])
            
            try:
                self.sheets_client.write_sheet('ProductionResult!A:G', decision_rows)
                print(f"  Decisions written to 'ProductionResult' tab")
            except Exception as e:
                print(f"  Warning: Could not write to sheet: {e}")
        except Exception as e:
            print(f"  Warning: Could not prepare decisions: {e}")

if __name__ == '__main__':
    orchestrator = Orchestrator()
    orchestrator.run()
