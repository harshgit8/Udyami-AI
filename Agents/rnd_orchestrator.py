from datetime import datetime
import config
from sheets_client import SheetsClient
from ai_client import AIClient
from agents.rnd_agent import RnDAgent

class RnDOrchestrator:
    def __init__(self):
        self.sheets_client = SheetsClient()
        self.ai_client = AIClient()
        self.rnd_agent = RnDAgent(self.ai_client)
    
    def run(self):
        print("Starting R&D Formulation Orchestration...")
        
        print("\n[1/3] Reading formulation requests from Google Sheets (RnD tab)...")
        try:
            raw_rows = self.sheets_client.read_sheet("RnD!A:H")
        except Exception as e:
            print(f"  Error: {e}")
            print("  Make sure 'RnD' sheet tab exists with formulation requests")
            return
        
        if not raw_rows or len(raw_rows) < 2:
            print("  No data found in RnD sheet")
            return
        
        headers = raw_rows[0]
        data_rows = raw_rows[1:]
        
        print(f"  Found {len(data_rows)} formulation requests")
        
        print("\n[2/3] Processing formulation requests...")
        results = []
        
        for idx, row in enumerate(data_rows, 1):
            if len(row) < 6:
                print(f"  Skipping row {idx}: insufficient data")
                continue
            
            request_id = row[0] if len(row) > 0 else f"REQ_{idx}"
            application = row[1] if len(row) > 1 else ""
            standards = row[2].split(',') if len(row) > 2 and row[2] else []
            cost_target = float(row[3]) if len(row) > 3 and row[3] else 100
            constraints = row[4].split(',') if len(row) > 4 and row[4] else []
            special_notes = row[5] if len(row) > 5 else ""
            tensile_min = float(row[6]) if len(row) > 6 and row[6] else 40
            chemical_resistance = row[7].split(',') if len(row) > 7 and row[7] else []
            
            requirements = {
                'application': application.strip(),
                'standards': [s.strip() for s in standards],
                'mechanical_requirements': {
                    'tensile_strength_min_mpa': tensile_min
                },
                'chemical_resistance': [c.strip() for c in chemical_resistance],
                'cost_target': cost_target,
                'constraints': [c.strip() for c in constraints],
                'special_notes': special_notes.strip()
            }
            
            print(f"  Processing: {request_id} - {application}")
            
            try:
                formulation_result = self.rnd_agent.design_formulation(requirements)
                formulation_result['request_id'] = request_id
                results.append(formulation_result)
                print(f"    ✓ Formulation generated: {formulation_result['formulation_id']}")
            except Exception as e:
                print(f"    ✗ Error: {e}")
                results.append({
                    'request_id': request_id,
                    'error': str(e),
                    'formulation_id': 'ERROR'
                })
        
        print(f"\n[3/3] Writing results to Google Sheets (RnDResult tab)...")
        self._write_results_to_sheet(results)
        
        report_file = f"{config.REPORTS_DIR}/rnd_formulations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self._save_detailed_report(results, report_file)
        print(f"  Detailed report saved: {report_file}")
        
        print("\n✓ R&D Orchestration complete!")
        return results
    
    def _write_results_to_sheet(self, results):
        try:
            output_rows = [[
                'Request ID',
                'Formulation ID',
                'Base Polymer',
                'Key Additives',
                'Cost (₹/kg)',
                'UL94 Rating',
                'Tensile (MPa)',
                'LOI (%)',
                'RoHS',
                'REACH',
                'Recommendation',
                'AI Confidence'
            ]]
            
            for result in results:
                if 'error' in result:
                    output_rows.append([
                        result['request_id'],
                        'ERROR',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        f"Error: {result['error']}",
                        ''
                    ])
                    continue
                
                comp = result['optimized_formulation']['composition_phr']
                base_polymer = [k for k in comp.keys() if 'PVC' in k or 'PP' in k or 'PE' in k]
                base_polymer = base_polymer[0] if base_polymer else 'Unknown'
                
                key_additives = [k for k in comp.keys() if k != base_polymer][:3]
                key_additives_str = ', '.join([k.replace('_', ' ') for k in key_additives])
                
                props = result['predicted_properties']
                compliance = result['compliance']
                ai = result['ai_insights']
                
                output_rows.append([
                    result['request_id'],
                    result['formulation_id'],
                    base_polymer.replace('_', ' '),
                    key_additives_str,
                    str(result['optimized_formulation']['cost_per_kg']),
                    props['ul94_rating'],
                    str(props['tensile_strength_mpa']),
                    str(props['loi_percent']),
                    str(compliance['rohs']),
                    str(compliance['reach']),
                    result['recommendation'],
                    ai.get('confidence_level', 'N/A')
                ])
            
            self.sheets_client.write_sheet('RnDResult!A:L', output_rows)
            print(f"  ✓ Results written to 'RnDResult' tab ({len(output_rows)-1} formulations)")
        
        except Exception as e:
            print(f"  ✗ Error writing to sheet: {e}")
    
    def _save_detailed_report(self, results, filename):
        lines = []
        lines.append("# 🧪 R&D Formulation Batch Report")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total Requests:** {len(results)}\n")
        lines.append("="*80 + "\n")
        
        for result in results:
            if 'error' in result:
                lines.append(f"## ❌ {result['request_id']} - ERROR")
                lines.append(f"**Error:** {result['error']}\n")
                lines.append("="*80 + "\n")
                continue
            
            report = self.rnd_agent.generate_report(result)
            lines.append(report)
            lines.append("\n" + "="*80 + "\n")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

if __name__ == '__main__':
    orchestrator = RnDOrchestrator()
    orchestrator.run()
