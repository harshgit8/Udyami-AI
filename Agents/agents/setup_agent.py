class SetupAgent:
    def __init__(self, setup_times):
        self.setup_times = setup_times
    
    def calculate_setup_times(self, orders, capacity_analysis):
        setup_analysis = []
        
        capacity_map = {c['order_id']: c for c in capacity_analysis}
        
        for order in orders:
            order_id = order['order_id']
            product_type = order['product_type']
            
            capacity = capacity_map.get(order_id, {})
            machine = capacity.get('best_machine', 'M1')
            
            setup_key = f"{machine}_{product_type}"
            setup_time = self.setup_times.get(setup_key, 1.5)
            
            setup_analysis.append({
                'order_id': order_id,
                'machine': machine,
                'product_type': product_type,
                'setup_time_hours': setup_time
            })
        
        return setup_analysis
