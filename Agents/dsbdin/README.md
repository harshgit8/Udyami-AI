# Manufacturing Audit Intelligence Platform

## 🏭 Overview

A comprehensive, AI-powered manufacturing audit and analytics platform that transforms Google Sheets data into actionable business intelligence. Built for manufacturing operations requiring detailed audit trails, compliance reporting, and cross-entity analysis.

## ✨ Key Features

### 🔄 Real-Time Data Synchronization
- **16 Google Sheets Integration**: Seamless sync from Production, Quality, R&D, Quotations, Invoices, and more
- **SQLite3 Database**: Optimized local storage with relationships and indexing
- **Live Updates**: Real-time data refresh with conflict resolution
- **Data Validation**: Automatic cleaning and type conversion

### 🤖 AI-Powered Analytics
- **Cross-Entity Correlation**: Intelligent analysis across all manufacturing processes
- **Predictive Insights**: Risk assessment and trend analysis
- **Pattern Recognition**: Anomaly detection and quality predictions
- **Natural Language Queries**: Ask questions in plain English

### 📊 Advanced Reporting
- **AI-Generated Reports**: Comprehensive markdown reports with insights
- **Multiple Report Types**: Production, Quality, Financial, R&D, Audit-ready
- **Interactive Dashboards**: Web-based visualization and filtering
- **Export Options**: PDF, Excel, JSON formats

### 🔍 Smart Filtering & Search
- **Multi-Dimensional Filtering**: Filter across all 16 data sources simultaneously
- **Saved Filter Profiles**: Pre-configured views for common audit scenarios
- **Global Search**: Find data across all tables with intelligent ranking
- **Dynamic Joins**: Visual relationship mapping between entities

### 💾 Intelligent Caching
- **Performance Optimization**: Sub-second response times for complex queries
- **Smart Cache Management**: TTL-based expiration and automatic cleanup
- **Report Caching**: Store generated reports for instant access
- **Memory Efficiency**: Optimized for large datasets

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Sheets API credentials
- Internet connection for initial sync

### Installation

1. **Clone and Setup**
```bash
cd dsbdin
pip install -r requirements.txt
```

2. **Configure Google Sheets Access**
```bash
# Copy your Google API credentials
cp ../creds.json ./creds.json
cp ../config.py ./config.py
```

3. **Initialize Database**
```bash
python test_platform.py
```

4. **Start Web Interface**
```bash
python web_interface.py
```

5. **Access Dashboard**
Open http://localhost:5000 in your browser

## 📋 Usage Guide

### 1. Data Synchronization
```python
from sheets_sync import SheetsSyncManager

sync_manager = SheetsSyncManager()
results = sync_manager.sync_all_sheets()
print(f"Synced {sum(results.values())} sheets successfully")
```

### 2. AI Analysis
```python
from ai_analyzer import AIAnalyzer

analyzer = AIAnalyzer()
insights = analyzer.generate_analysis('production', {'priority': 'high'})
print(f"Found {insights['high_risk_orders']} high-risk orders")
```

### 3. Report Generation
```python
from report_generator import ReportGenerator

report_gen = ReportGenerator()
report = report_gen.generate_report('comprehensive', save_to_file=True)
print(f"Report saved to: {report['saved_to']}")
```

### 4. Web Interface
- **Dashboard**: Overview of all systems and quick actions
- **Data Explorer**: Browse and search manufacturing data
- **Analysis Tools**: Run AI analysis with custom filters
- **Report Builder**: Generate and download reports
- **Cache Management**: Monitor and clear cached data

## 🏗️ Architecture

### Core Components

```
Manufacturing Audit Intelligence Platform
├── Database Layer (SQLite3)
│   ├── Production Tables (Orders, Results)
│   ├── Quality Tables (Inspections, Results)
│   ├── Financial Tables (Quotes, Invoices)
│   ├── R&D Tables (Requests, Formulations)
│   └── Cache Tables (Report Storage)
├── Sync Engine
│   ├── Google Sheets Client
│   ├── Data Transformation
│   ├── Conflict Resolution
│   └── Real-time Updates
├── AI Analytics Engine
│   ├── Cross-Entity Analysis
│   ├── Pattern Recognition
│   ├── Predictive Modeling
│   └── Insight Generation
├── Report Generator
│   ├── Template Engine
│   ├── AI Commentary
│   ├── Export Formats
│   └── Audit Compliance
└── Web Interface
    ├── Interactive Dashboard
    ├── Data Visualization
    ├── Filter Management
    └── Real-time Updates
```

### Data Flow

1. **Google Sheets** → **Sync Engine** → **SQLite Database**
2. **Database** → **AI Analyzer** → **Insights & Patterns**
3. **Insights** → **Report Generator** → **Formatted Reports**
4. **All Components** → **Web Interface** → **User Dashboard**

## 📊 Supported Data Types

### Production Data
- Orders, priorities, customers, due dates
- Production decisions, risk scores, machine assignments
- Capacity planning and scheduling

### Quality Data
- Batch inspections, defect tracking
- Pass/fail rates, compliance standards
- Statistical quality control

### Financial Data
- Quotations, pricing, cost analysis
- Invoices, revenue tracking
- Profit margin analysis

### R&D Data
- Formulation requests, material specifications
- Compliance testing (RoHS, REACH)
- Cost optimization

## 🔧 Configuration

### Environment Variables
```bash
# Google Sheets Configuration
GOOGLE_SHEETS_ID="your_sheet_id_here"
GOOGLE_API_CREDENTIALS="path/to/creds.json"

# Database Configuration
DATABASE_PATH="audit_intelligence.db"
CACHE_TTL_HOURS=24

# Web Interface
FLASK_HOST="0.0.0.0"
FLASK_PORT=5000
FLASK_DEBUG=True
```

### Custom Filters
```python
# Example: High-priority orders with quality issues
filters = {
    'priority': 'high',
    'date_from': '2026-01-01',
    'defect_rate_min': 5.0
}

insights = analyzer.generate_analysis('cross_analysis', filters)
```

## 🧪 Testing

### Comprehensive Test Suite
```bash
python test_platform.py
```

**Test Coverage:**
- ✅ Database initialization and schema validation
- ✅ Google Sheets synchronization
- ✅ AI analysis accuracy and performance
- ✅ Report generation and formatting
- ✅ Caching system efficiency
- ✅ Web interface functionality
- ✅ Performance benchmarks

### Performance Benchmarks
- **Database Queries**: < 1 second for complex joins
- **AI Analysis**: < 5 seconds for full dataset
- **Report Generation**: < 10 seconds for comprehensive reports
- **Cache Hit Rate**: > 90% for repeated queries

## 📈 Analytics Capabilities

### Production Analytics
- Order volume trends and forecasting
- Priority distribution and risk assessment
- Customer demand patterns
- Machine utilization optimization

### Quality Analytics
- Defect rate analysis and trending
- Compliance monitoring and alerts
- Statistical process control
- Root cause analysis

### Financial Analytics
- Revenue tracking and forecasting
- Cost variance analysis
- Profit margin optimization
- Customer profitability

### Cross-Entity Intelligence
- Production-Quality correlations
- Quote-to-Invoice accuracy
- Customer lifecycle analysis
- Supply chain optimization

## 🛡️ Security & Compliance

### Data Security
- Local SQLite database (no cloud storage)
- Encrypted API communications
- Access logging and audit trails
- Data validation and sanitization

### Audit Compliance
- Complete transaction traceability
- Regulatory compliance reporting
- Digital signatures for reports
- Historical data preservation

## 🚀 Deployment

### Local Development
```bash
python web_interface.py
# Access: http://localhost:5000
```

### Production Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_interface:app

# Using Docker
docker build -t manufacturing-audit .
docker run -p 5000:5000 manufacturing-audit
```

## 📚 API Reference

### Sync Endpoints
- `POST /api/sync` - Sync all sheets
- `GET /api/sync/status` - Get sync status

### Analysis Endpoints
- `GET /api/analyze/<type>` - Run analysis
- `GET /api/analyze/<type>?filters={}` - Filtered analysis

### Report Endpoints
- `GET /api/report/<type>` - Generate report
- `GET /api/reports/list` - List available reports

### Data Endpoints
- `GET /api/data/<table>` - Get table data
- `GET /api/search?q=<query>` - Search across tables
- `GET /api/tables` - List all tables

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Run test suite
4. Submit pull request

### Code Standards
- Python PEP 8 compliance
- Comprehensive error handling
- Performance optimization
- Security best practices

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

### Documentation
- API documentation: `/docs`
- User guide: `/help`
- Video tutorials: Available on request

### Contact
- Technical support: Create GitHub issue
- Feature requests: Submit enhancement proposal
- Security issues: Contact maintainers directly

---

**Built with ❤️ for Manufacturing Excellence**

*Transform your manufacturing data into actionable intelligence with the power of AI.*