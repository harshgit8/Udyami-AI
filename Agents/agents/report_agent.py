from datetime import datetime
import json

class ReportAgent:
    def __init__(self, gemini_client):
        self.gemini = gemini_client
    
    def generate_report(self, orders, schedule, structured_tasks):
        decisions = self._create_decisions(orders, schedule, structured_tasks)
        
        decisions_with_ai = self._enhance_with_ai_reasoning(decisions, structured_tasks)
        
        report_lines = []
        report_lines.append("# 🏭 AI Production Schedule Report")
        report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        report_lines.append("## 📊 Executive Summary")
        total_orders = len(orders)
        scheduled = len([d for d in decisions_with_ai if d['decision'] == 'PROCEED'])
        delayed = len([d for d in decisions_with_ai if d['decision'] == 'DELAY'])
        rejected = len([d for d in decisions_with_ai if d['decision'] == 'REJECT'])
        
        report_lines.append(f"- **Total Orders Analyzed:** {total_orders}")
        report_lines.append(f"- ✅ **Scheduled for Production:** {scheduled}")
        report_lines.append(f"- ⚠️ **Delayed:** {delayed}")
        report_lines.append(f"- ❌ **Rejected:** {rejected}\n")
        
        report_lines.append("## 🎯 Order Decisions\n")
        
        for decision in decisions_with_ai:
            emoji = {'PROCEED': '✅', 'DELAY': '⚠️', 'REJECT': '❌'}.get(decision['decision'], '•')
            report_lines.append(f"### {emoji} Order {decision['order_id']}")
            report_lines.append(f"- **Decision:** {decision['decision']}")
            report_lines.append(f"- **Risk Score:** {decision['risk_score']}/10")
            report_lines.append(f"- **Reason:** {decision['reason']}")
            
            if decision.get('ai_explanation'):
                report_lines.append(f"- **AI Analysis:** {decision['ai_explanation']}")
            
            if decision['decision'] == 'PROCEED':
                report_lines.append(f"- **Machine:** {decision.get('machine', 'N/A')}")
                report_lines.append(f"- **Start Time:** {decision.get('start_time', 'N/A')[:19]}")
                report_lines.append(f"- **End Time:** {decision.get('end_time', 'N/A')[:19]}")
            
            if decision.get('recommendation'):
                report_lines.append(f"- **💡 Recommendation:** {decision['recommendation']}")
            
            report_lines.append("")
        
        return "\n".join(report_lines), decisions_with_ai
    
    def _create_decisions(self, orders, schedule, structured_tasks):
        schedule_map = {s['task_id']: s for s in schedule}
        task_map = {t['task_id']: t for t in structured_tasks}
        
        decisions = []
        
        for order in orders:
            order_id = order['order_id']
            task = task_map.get(order_id)
            scheduled_item = schedule_map.get(order_id)
            
            if not task:
                decisions.append({
                    'order_id': order_id,
                    'decision': 'REJECT',
                    'reason': 'No capable machine available',
                    'risk_score': 10
                })
                continue
            
            if not task['materials_ready']:
                decisions.append({
                    'order_id': order_id,
                    'decision': 'DELAY',
                    'reason': f"Material shortages: {', '.join([s['material'] for s in task['materials_shortages']])}",
                    'risk_score': 7
                })
                continue
            
            if not task['feasible']:
                decisions.append({
                    'order_id': order_id,
                    'decision': 'DELAY',
                    'reason': f"Insufficient time to meet deadline (slack: {task['slack_days']} days)",
                    'risk_score': 8
                })
                continue
            
            if scheduled_item:
                risk_score = self._calculate_risk(task)
                decisions.append({
                    'order_id': order_id,
                    'decision': 'PROCEED',
                    'reason': 'All constraints satisfied',
                    'risk_score': risk_score,
                    'machine': scheduled_item['machine'],
                    'start_time': scheduled_item['start_time'],
                    'end_time': scheduled_item['end_time']
                })
            else:
                decisions.append({
                    'order_id': order_id,
                    'decision': 'DELAY',
                    'reason': 'Could not fit in schedule',
                    'risk_score': 6
                })
        
        return decisions
    
    def _calculate_risk(self, task):
        risk = 0
        
        if task['urgency'] == 'critical':
            risk += 3
        elif task['urgency'] == 'high':
            risk += 2
        
        if task['slack_days'] < 2:
            risk += 3
        elif task['slack_days'] < 5:
            risk += 1
        
        return min(risk, 10)

    def _enhance_with_ai_reasoning(self, decisions, structured_tasks):
        task_map = {t['task_id']: t for t in structured_tasks}
        
        for decision in decisions:
            order_id = decision['order_id']
            task = task_map.get(order_id, {})
            
            try:
                prompt = self._build_reasoning_prompt(decision, task)
                ai_response = self.gemini.generate_json(prompt, temperature=0.2)
                
                decision['ai_explanation'] = ai_response.get('explanation', '')
                decision['recommendation'] = ai_response.get('recommendation', '')
                
                if 'risk_factors' in ai_response:
                    decision['risk_factors'] = ai_response['risk_factors']
            except Exception as e:
                decision['ai_explanation'] = f"AI analysis unavailable: {str(e)}"
        
        return decisions
    
    def _build_reasoning_prompt(self, decision, task):
        prompt = f"""You are a production scheduling AI assistant. Analyze this order decision and provide insights.

Order ID: {decision['order_id']}
Decision: {decision['decision']}
Current Reason: {decision['reason']}
Risk Score: {decision['risk_score']}/10

Context:
- Product Type: {task.get('product_type', 'N/A')}
- Quantity: {task.get('quantity', 'N/A')}
- Urgency: {task.get('urgency', 'N/A')}
- Materials Ready: {task.get('materials_ready', 'N/A')}
- Feasible: {task.get('feasible', 'N/A')}
- Slack Days: {task.get('slack_days', 'N/A')}

Provide a JSON response with:
{{
  "explanation": "Brief 1-2 sentence explanation of why this decision was made",
  "recommendation": "Actionable recommendation for the production manager",
  "risk_factors": ["list", "of", "key", "risk", "factors"]
}}

Keep it concise and practical for factory managers."""
        
        return prompt
