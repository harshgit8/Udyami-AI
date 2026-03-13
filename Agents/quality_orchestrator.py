from datetime import datetime
import config
from sheets_client import SheetsClient
from ai_client import AIClient
from agents.quality_agent import QualityAgent

class QualityOrchestrator:
    def __init__(self):
        self.sheets_client = SheetsClient()
        self.ai_client = AIClient()
        self.quality_agent = QualityAgent(self.ai_client)
    
    def run(self):
        print("Starting Quality Inspection Orchestration...")
        
        print("\n[1/3] Reading inspection data from Google Sheets (Quality tab)...")
        try:
            raw_rows = self.sheets_client.read_sheet("Quality!A:H")
        except Exception as e:
            print(f"  Error: {e}")
            print("  Make sure 'Quality' sheet tab exists with inspection data")
            return
        
        if not raw_rows or len(raw_rows) < 2:
            print("  No data found in Quality sheet")
            return
        
        headers = raw_rows[0]
        data_rows = raw_rows[1:]
        
        print(f"  Found {len(data_rows)} inspection records")
        
        print("\n[2/3] Processing quality inspections...")
        results = []
        
        for idx, row in enumerate(data_rows, 1):
            if len(row) < 4:
                print(f"  Skipping row {idx}: insufficient data")
                continue
            
            batch_id = row[0] if len(row) > 0 else f"BATCH_{idx}"
            product_type = row[1] if len(row) > 1 else ""
            quantity = int(row[2]) if len(row) > 2 and row[2] else 0
            inspection_standard = row[3] if len(row) > 3 else "ISO_2859"
            defects_raw = row[4] if len(row) > 4 else ""
            measurements_raw = row[5] if len(row) > 5 else ""
            visual_inspection = row[6] if len(row) > 6 else ""
            special_requirements = row[7] if len(row) > 7 else ""
            
            defects_found = self._parse_defects(defects_raw)
            measurements = self._parse_measurements(measurements_raw)
            
            inspection_data = {
                'batch_id': batch_id.strip(),
                'product_type': product_type.strip(),
                'quantity': quantity,
                'inspection_standard': inspection_standard.strip(),
                'defects_found': defects_found,
                'measurements': measurements,
                'visual_inspection': visual_inspection.strip(),
                'special_requirements': special_requirements.strip()
            }
            
            print(f"  Inspecting: {batch_id} - {product_type} ({quantity} units)")
            
            try:
                inspection_result = self.quality_agent.inspect_batch(inspection_data)
                results.append(inspection_result)
                decision = inspection_result['final_decision']['decision']
                emoji = {'ACCEPT': '✅', 'REJECT': '❌', 'CONDITIONAL_ACCEPT': '⚠️'}.get(decision, '•')
                print(f"    {emoji} {decision}")
            except Exception as e:
                print(f"    ✗ Error: {e}")
                results.append({
                    'batch_id': batch_id,
                    'error': str(e),
                    'inspection_id': 'ERROR',
                    'final_decision': {'decision': 'ERROR', 'reason': str(e), 'confidence': 0}
                })
        
        print(f"\n[3/3] Writing results to Google Sheets (QualityResult tab)...")
        self._write_results_to_sheet(results)
        
        report_file = f"{config.REPORTS_DIR}/quality_inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self._save_detailed_report(results, report_file)
        print(f"  Detailed report saved: {report_file}")
        
        print("\n✓ Quality Orchestration complete!")
        return results
    
    def _parse_defects(self, defects_raw):
        """Parse defects from format: type:severity:count,type:severity:count"""
        if not defects_raw:
            return []
        
        defects = []
        for defect_str in defects_raw.split(','):
            parts = defect_str.strip().split(':')
            if len(parts) >= 3:
                defect_type = parts[0]
                severity = parts[1]
                count = int(parts[2])
                
                for _ in range(count):
                    defects.append({
                        'type': defect_type,
                        'severity': severity
                    })
        
        return defects
    
    def _parse_measurements(self, measurements_raw):
        """Parse measurements from format: param:value,param:value"""
        if not measurements_raw:
            return {}
        
        measurements = {}
        for meas_str in measurements_raw.split(','):
            parts = meas_str.strip().split(':')
            if len(parts) == 2:
                param = parts[0]
                try:
                    value = float(parts[1])
                    measurements[param] = value
                except ValueError:
                    pass
        
        return measurements
    
    def _write_results_to_sheet(self, results):
        try:
            output_rows = [[
                'Batch ID',
                'Inspection ID',
                'Product Type',
                'Quantity',
                'Total Defects',
                'Critical',
                'Major',
                'Minor',
                'Defect Rate %',
                'Severity Level',
                'Risk Level',
                'Decision',
                'Confidence %',
                'Recommendation'
            ]]
            
            for result in results:
                if 'error' in result:
                    output_rows.append([
                        result['batch_id'],
                        'ERROR',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        'ERROR',
                        '0',
                        f"Error: {result['error']}"
                    ])
                    continue
                
                defects = result['defect_analysis']
                severity = result['severity_assessment']
                decision = result['final_decision']
                
                output_rows.append([
                    result['batch_id'],
                    result['inspection_id'],
                    result['product_type'],
                    str(result['quantity']),
                    str(defects['total_defects']),
                    str(defects['critical_count']),
                    str(defects['major_count']),
                    str(defects['minor_count']),
                    str(defects['defect_rate_percent']),
                    severity['severity_level'],
                    severity['risk_level'],
                    decision['decision'],
                    str(decision['confidence']),
                    result['recommendation']
                ])
            
            self.sheets_client.write_sheet('QualityResult!A:N', output_rows)
            print(f"  ✓ Results written to 'QualityResult' tab ({len(output_rows)-1} inspections)")
        
        except Exception as e:
            print(f"  ✗ Error writing to sheet: {e}")
    
    def _save_detailed_report(self, results, filename):
        lines = []
        lines.append("# 🔍 Quality Inspection Batch Report")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total Inspections:** {len(results)}\n")
        
        accept_count = sum(1 for r in results if r.get('final_decision', {}).get('decision') == 'ACCEPT')
        reject_count = sum(1 for r in results if r.get('final_decision', {}).get('decision') == 'REJECT')
        conditional_count = sum(1 for r in results if r.get('final_decision', {}).get('decision') == 'CONDITIONAL_ACCEPT')
        
        lines.append("## Summary")
        lines.append(f"- ✅ **Accepted:** {accept_count}")
        lines.append(f"- ❌ **Rejected:** {reject_count}")
        lines.append(f"- ⚠️ **Conditional:** {conditional_count}\n")
        lines.append("="*80 + "\n")
        
        for result in results:
            if 'error' in result:
                lines.append(f"## ❌ {result['batch_id']} - ERROR")
                lines.append(f"**Error:** {result['error']}\n")
                lines.append("="*80 + "\n")
                continue
            
            report = self.quality_agent.generate_report(result)
            lines.append(report)
            lines.append("\n" + "="*80 + "\n")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

if __name__ == '__main__':
    orchestrator = QualityOrchestrator()
    orchestrator.run()
