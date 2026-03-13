from datetime import datetime, timedelta

class CapacityAgent:
    def __init__(self, machines_config):
        self.machines = machines_config
    
    def check_capacity(self, orders):
        capacity_analysis = []
        
        for order in orders:
            product_type = order['product_type']
            quantity = order['quantity']
            
            capable_machines = self._find_capable_machines(product_type)
            
            if not capable_machines:
                capacity_analysis.append({
                    'order_id': order['order_id'],
                    'status': 'NO_MACHINE',
                    'capable_machines': [],
                    'estimated_time_hours': 0,
                    'message': f"No machine can produce {product_type}"
                })
                continue
            
            best_machine = min(capable_machines, 
                             key=lambda m: m['production_rate'])
            
            production_time = quantity / best_machine['production_rate']
            
            capacity_analysis.append({
                'order_id': order['order_id'],
                'status': 'OK',
                'capable_machines': [m['machine_id'] for m in capable_machines],
                'best_machine': best_machine['machine_id'],
                'estimated_time_hours': round(production_time, 2),
                'production_rate': best_machine['production_rate']
            })
        
        return capacity_analysis
    
    def _find_capable_machines(self, product_type):
        return [m for m in self.machines 
                if product_type in m.get('capable_products', [])]
