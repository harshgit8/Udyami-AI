from datetime import datetime

class OrdersAgent:
    def __init__(self):
        self.validation_errors = []
    
    def validate_and_clean(self, raw_rows):
        """Validate and clean order data from sheets"""
        if not raw_rows or len(raw_rows) < 2:
            return []
        
        headers = raw_rows[0]
        data_rows = raw_rows[1:]
        
        orders = []
        self.validation_errors = []
        
        for idx, row in enumerate(data_rows, start=2):
            if len(row) < 6:
                self.validation_errors.append(f"Row {idx}: Insufficient columns")
                continue
            
            try:
                order = {
                    'order_id': row[0] if len(row) > 0 else f"ORD-{idx}",
                    'product_type': row[1] if len(row) > 1 else "",
                    'quantity': int(row[2]) if len(row) > 2 and row[2] else 0,
                    'due_date': row[3] if len(row) > 3 else "",
                    'priority': row[4].lower() if len(row) > 4 else "normal",
                    'customer': row[5] if len(row) > 5 else "",
                    'notes': row[6] if len(row) > 6 else ""
                }
                
                if order['quantity'] <= 0:
                    self.validation_errors.append(f"Row {idx}: Invalid quantity")
                    continue
                
                orders.append(order)
            except Exception as e:
                self.validation_errors.append(f"Row {idx}: {str(e)}")
        
        return orders
