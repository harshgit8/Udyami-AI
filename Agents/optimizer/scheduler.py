from datetime import datetime, timedelta

class ProductionScheduler:
    def __init__(self, machines_config):
        self.machines = {m['machine_id']: m for m in machines_config}
        self.machine_schedules = {m['machine_id']: [] for m in machines_config}
    
    def optimize(self, structured_tasks):
        """Simple greedy scheduler - schedules tasks by priority and deadline"""
        
        # Filter feasible tasks with materials
        feasible_tasks = [t for t in structured_tasks 
                         if t['feasible'] and t['materials_ready'] and t['capable_machines']]
        
        # Sort by urgency and slack days
        urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        feasible_tasks.sort(key=lambda t: (urgency_order.get(t['urgency'], 4), t['slack_days']))
        
        schedule = []
        current_time = datetime.now()
        
        for task in feasible_tasks:
            best_machine = self._find_best_machine(task, current_time)
            
            if best_machine:
                machine_id = best_machine['machine_id']
                
                # Get last end time for this machine
                machine_tasks = [s for s in schedule if s['machine'] == machine_id]
                if machine_tasks:
                    start_time = max(datetime.fromisoformat(s['end_time']) for s in machine_tasks)
                else:
                    start_time = current_time
                
                # Add setup time
                start_time += timedelta(hours=task['setup_time_hours'])
                
                # Calculate end time
                end_time = start_time + timedelta(hours=task['production_time_hours'])
                
                schedule.append({
                    'task_id': task['task_id'],
                    'machine': machine_id,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'product_type': task['product_type'],
                    'quantity': task['quantity']
                })
        
        return schedule
    
    def _find_best_machine(self, task, current_time):
        """Find best available machine for task"""
        capable_machines = [self.machines[m] for m in task['capable_machines'] 
                           if m in self.machines]
        
        if not capable_machines:
            return None
        
        # Return machine with highest production rate (fastest)
        return max(capable_machines, key=lambda m: m['production_rate'])
