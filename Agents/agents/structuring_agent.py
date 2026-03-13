class StructuringAgent:
    def __init__(self):
        pass
    
    def structure_for_optimizer(self, orders, capacity_analysis, materials_status, 
                                deadlines_analysis, setup_analysis):
        capacity_map = {c['order_id']: c for c in capacity_analysis}
        materials_map = {m['order_id']: m for m in materials_status}
        deadlines_map = {d['order_id']: d for d in deadlines_analysis}
        setup_map = {s['order_id']: s for s in setup_analysis}
        
        structured_tasks = []
        
        for order in orders:
            order_id = order['order_id']
            
            capacity = capacity_map.get(order_id, {})
            materials = materials_map.get(order_id, {})
            deadline = deadlines_map.get(order_id, {})
            setup = setup_map.get(order_id, {})
            
            task = {
                'task_id': order_id,
                'product_type': order['product_type'],
                'quantity': order['quantity'],
                'priority': order['priority'],
                'customer': order['customer'],
                'capable_machines': capacity.get('capable_machines', []),
                'best_machine': capacity.get('best_machine', ''),
                'production_time_hours': capacity.get('estimated_time_hours', 0),
                'setup_time_hours': setup.get('setup_time_hours', 0),
                'materials_ready': materials.get('ready', False),
                'materials_shortages': materials.get('shortages', []),
                'due_date': deadline.get('due_date', ''),
                'days_until_due': deadline.get('days_until_due', 0),
                'slack_days': deadline.get('slack_days', 0),
                'urgency': deadline.get('urgency', 'low'),
                'feasible': deadline.get('feasible', True)
            }
            
            structured_tasks.append(task)
        
        return structured_tasks
