from datetime import datetime

class WebAgent:
    def __init__(self):
        pass
    
    def generate_html(self, schedule, decisions):
        """Generate HTML visualization of schedule"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Production Schedule - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .schedule {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .task {{ border-left: 4px solid #4CAF50; padding: 10px; margin: 10px 0; background: #f9f9f9; }}
        .task.delay {{ border-left-color: #FF9800; }}
        .task.reject {{ border-left-color: #F44336; }}
        .machine {{ font-weight: bold; color: #2196F3; }}
        .time {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>🏭 Production Schedule</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="schedule">
        <h2>Scheduled Tasks</h2>
"""
        
        for item in schedule:
            html += f"""
        <div class="task">
            <strong>Order: {item['task_id']}</strong><br>
            <span class="machine">Machine: {item['machine']}</span><br>
            <span class="time">Start: {item['start_time'][:19]}</span><br>
            <span class="time">End: {item['end_time'][:19]}</span>
        </div>
"""
        
        html += """
    </div>
    
    <div class="schedule">
        <h2>All Decisions</h2>
"""
        
        for decision in decisions:
            css_class = decision['decision'].lower()
            html += f"""
        <div class="task {css_class}">
            <strong>Order: {decision['order_id']}</strong><br>
            Decision: {decision['decision']}<br>
            Reason: {decision['reason']}<br>
            Risk Score: {decision['risk_score']}/10
        </div>
"""
        
        html += """
    </div>
</body>
</html>"""
        
        return html
