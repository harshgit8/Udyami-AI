from datetime import datetime, timedelta

class DeadlinesAgent:
    def __init__(self):
        pass
    
    def analyze_deadlines(self, orders, capacity_analysis):
        deadline_analysis = []
        
        capacity_map = {c['order_id']: c for c in capacity_analysis}
        
        for order in orders:
            order_id = order['order_id']
            due_date_str = order.get('due_date', '')
            
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except:
                due_date = datetime.now() + timedelta(days=30)
            
            capacity = capacity_map.get(order_id, {})
            estimated_hours = capacity.get('estimated_time_hours', 0)
            
            days_until_due = (due_date - datetime.now()).days
            estimated_days = estimated_hours / 8
            slack_days = days_until_due - estimated_days
            
            if slack_days < 0:
                urgency = 'critical'
                feasible = False
            elif slack_days < 2:
                urgency = 'high'
                feasible = True
            elif slack_days < 5:
                urgency = 'medium'
                feasible = True
            else:
                urgency = 'low'
                feasible = True
            
            deadline_analysis.append({
                'order_id': order_id,
                'due_date': due_date_str,
                'days_until_due': days_until_due,
                'estimated_days': round(estimated_days, 1),
                'slack_days': round(slack_days, 1),
                'urgency': urgency,
                'feasible': feasible
            })
        
        return deadline_analysis
