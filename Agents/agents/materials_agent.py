from datetime import datetime, timedelta

class MaterialsAgent:
    def __init__(self, gemini_client, materials_inventory):
        self.gemini = gemini_client
        self.inventory = materials_inventory
    
    def check_materials(self, orders):
        materials_status = []
        
        for order in orders:
            product_type = order['product_type']
            quantity = order['quantity']
            
            required_materials = self._get_bom(product_type, quantity)
            availability = self._check_availability(required_materials)
            
            if availability['all_available']:
                materials_status.append({
                    'order_id': order['order_id'],
                    'status': 'AVAILABLE',
                    'shortages': [],
                    'ready': True
                })
            else:
                materials_status.append({
                    'order_id': order['order_id'],
                    'status': 'SHORTAGE',
                    'shortages': availability['shortages'],
                    'ready': False,
                    'estimated_ready_date': availability.get('estimated_ready_date')
                })
        
        return materials_status
    
    def _get_bom(self, product_type, quantity):
        bom_map = {
            'widget_a': {'steel': 2, 'plastic': 1},
            'widget_b': {'steel': 1, 'aluminum': 3},
            'widget_c': {'plastic': 5, 'copper': 2}
        }
        
        bom = bom_map.get(product_type.lower(), {})
        return {mat: qty * quantity for mat, qty in bom.items()}
    
    def _check_availability(self, required_materials):
        shortages = []
        all_available = True
        
        for material, required_qty in required_materials.items():
            available_qty = self.inventory.get(material, 0)
            if available_qty < required_qty:
                all_available = False
                shortages.append({
                    'material': material,
                    'required': required_qty,
                    'available': available_qty,
                    'shortage': required_qty - available_qty
                })
        
        result = {
            'all_available': all_available,
            'shortages': shortages
        }
        
        if not all_available:
            result['estimated_ready_date'] = (
                datetime.now() + timedelta(days=7)
            ).isoformat()
        
        return result
