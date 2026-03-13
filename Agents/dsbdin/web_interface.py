#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, send_file
from sheets_sync import SheetsSyncManager
from ai_analyzer import AIAnalyzer
from report_generator import ReportGenerator
from database_manager import DatabaseManager
import json
from datetime import datetime
import logging
from typing import Dict, List, Any

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'manufacturing_audit_intelligence_2026'

# Initialize components
sync_manager = SheetsSyncManager()
ai_analyzer = AIAnalyzer()
report_generator = ReportGenerator()
db_manager = DatabaseManager()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main dashboard"""
    return dashboard_template()

@app.route('/api/sync', methods=['POST'])
def sync_data():
    """Sync data from Google Sheets"""
    try:
        results = sync_manager.sync_all_sheets()
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        return jsonify({
            'success': True,
            'message': f'Synced {success_count}/{total_count} sheets successfully',
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sync/status')
def sync_status():
    """Get sync status"""
    try:
        status = sync_manager.get_sync_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze/<analysis_type>')
def analyze_data(analysis_type):
    """Perform data analysis"""
    try:
        # Get filters from query parameters
        filters = {}
        for key, value in request.args.items():
            if value:
                filters[key] = value
        
        # Generate analysis
        insights = ai_analyzer.generate_analysis(analysis_type, filters)
        
        return jsonify({
            'success': True,
            'analysis_type': analysis_type,
            'insights': insights,
            'filters': filters
        })
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/report/<report_type>')
def generate_report(report_type):
    """Generate report"""
    try:
        # Get filters from query parameters
        filters = {}
        for key, value in request.args.items():
            if value and key != 'save':
                filters[key] = value
        
        # Check if should save to file
        save_to_file = request.args.get('save', 'true').lower() == 'true'
        
        # Generate report
        result = report_generator.generate_report(report_type, filters, save_to_file)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reports/list')
def list_reports():
    """List available report types"""
    try:
        reports = report_generator.list_available_reports()
        return jsonify({
            'success': True,
            'reports': reports
        })
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/data/<table_name>')
def get_table_data(table_name):
    """Get data from specific table"""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        offset = (page - 1) * per_page
        
        # Get filters
        filters = {}
        where_conditions = []
        params = []
        
        for key, value in request.args.items():
            if key not in ['page', 'per_page'] and value:
                where_conditions.append(f"{key} LIKE ?")
                params.append(f"%{value}%")
                filters[key] = value
        
        # Build query
        base_query = f"SELECT * FROM {table_name}"
        count_query = f"SELECT COUNT(*) as total FROM {table_name}"
        
        if where_conditions:
            where_clause = " WHERE " + " AND ".join(where_conditions)
            base_query += where_clause
            count_query += where_clause
        
        base_query += f" LIMIT {per_page} OFFSET {offset}"
        
        # Execute queries
        data = db_manager.query(base_query, tuple(params))
        count_result = db_manager.query(count_query, tuple(params))
        total = count_result[0]['total'] if count_result else 0
        
        return jsonify({
            'success': True,
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            },
            'filters': filters
        })
    except Exception as e:
        logger.error(f"Data retrieval failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tables')
def list_tables():
    """List all available tables"""
    try:
        tables = list(sync_manager.sheet_mappings.values())
        table_info = {}
        
        for table in tables:
            info = db_manager.get_table_info(table)
            table_info[table] = {
                'row_count': info.get('row_count', 0),
                'columns': [col['name'] for col in info.get('columns', [])]
            }
        
        return jsonify({
            'success': True,
            'tables': table_info
        })
    except Exception as e:
        logger.error(f"Failed to list tables: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search')
def search_data():
    """Search across all tables"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        results = {}
        tables = list(sync_manager.sheet_mappings.values())
        
        for table in tables:
            # Get table info to know which columns to search
            table_info = db_manager.get_table_info(table)
            columns = [col['name'] for col in table_info.get('columns', [])]
            
            # Build search query for text columns
            text_columns = [col for col in columns if col not in ['id', 'created_at', 'updated_at']]
            if text_columns:
                search_conditions = []
                params = []
                
                for col in text_columns[:5]:  # Limit to first 5 columns
                    search_conditions.append(f"{col} LIKE ?")
                    params.append(f"%{query}%")
                
                if search_conditions:
                    search_query = f"""
                    SELECT * FROM {table} 
                    WHERE {' OR '.join(search_conditions)}
                    LIMIT 10
                    """
                    
                    data = db_manager.query(search_query, tuple(params))
                    if data:
                        results[table] = data
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total_tables': len(results)
        })
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cache/clear')
def clear_cache():
    """Clear analysis cache"""
    try:
        cache_tables = [
            'production_reports_cache',
            'quality_reports_cache',
            'quotation_reports_cache',
            'invoice_reports_cache',
            'rnd_reports_cache',
            'schedule_reports_cache'
        ]
        
        cleared = 0
        for table in cache_tables:
            if db_manager.execute(f"DELETE FROM {table}"):
                cleared += 1
        
        return jsonify({
            'success': True,
            'message': f'Cleared {cleared} cache tables',
            'cleared_tables': cleared
        })
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# HTML Templates (embedded for simplicity)
def dashboard_template():
    """Dashboard template"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manufacturing Audit Intelligence Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .card h3 { color: #333; margin-bottom: 15px; font-size: 1.3em; }
        .btn { background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 1em; margin: 5px; }
        .btn:hover { background: #5a6fd8; }
        .btn.secondary { background: #6c757d; }
        .btn.success { background: #28a745; }
        .btn.danger { background: #dc3545; }
        .status { padding: 10px; border-radius: 6px; margin: 10px 0; }
        .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .status.info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .loading { display: none; text-align: center; padding: 20px; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .results { background: white; padding: 20px; border-radius: 10px; margin-top: 20px; }
        .table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        .table th { background: #f8f9fa; font-weight: 600; }
        .filters { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .filter-input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 Manufacturing Audit Intelligence</h1>
            <p>Advanced Analytics & Reporting Platform for Manufacturing Operations</p>
        </div>

        <div class="grid">
            <div class="card">
                <h3>📊 Data Synchronization</h3>
                <p>Sync data from Google Sheets (16 tabs) to local database for analysis.</p>
                <button class="btn" onclick="syncData()">Sync All Data</button>
                <button class="btn secondary" onclick="getSyncStatus()">Check Status</button>
                <button class="btn danger" onclick="clearCache()">Clear Cache</button>
                <div id="sync-status"></div>
            </div>

            <div class="card">
                <h3>🔍 Data Analysis</h3>
                <p>Perform AI-powered analysis on manufacturing data.</p>
                <select id="analysis-type" class="filter-input">
                    <option value="production">Production Analysis</option>
                    <option value="quality">Quality Analysis</option>
                    <option value="quotation">Quotation Analysis</option>
                    <option value="invoice">Invoice Analysis</option>
                    <option value="rnd">R&D Analysis</option>
                    <option value="cross_analysis">Cross-Entity Analysis</option>
                </select>
                <button class="btn" onclick="runAnalysis()">Run Analysis</button>
                <div id="analysis-results"></div>
            </div>

            <div class="card">
                <h3>📋 Report Generation</h3>
                <p>Generate comprehensive reports with AI insights.</p>
                <select id="report-type" class="filter-input">
                    <option value="production">Production Report</option>
                    <option value="quality">Quality Report</option>
                    <option value="quotation">Quotation Report</option>
                    <option value="invoice">Invoice Report</option>
                    <option value="rnd">R&D Report</option>
                    <option value="comprehensive">Comprehensive Report</option>
                    <option value="audit">Audit Report</option>
                </select>
                <button class="btn success" onclick="generateReport()">Generate Report</button>
                <div id="report-results"></div>
            </div>

            <div class="card">
                <h3>🗃️ Data Explorer</h3>
                <p>Browse and search through manufacturing data.</p>
                <select id="table-select" class="filter-input">
                    <option value="">Select Table...</option>
                </select>
                <input type="text" id="search-query" placeholder="Search..." class="filter-input">
                <button class="btn" onclick="loadTableData()">Load Data</button>
                <button class="btn secondary" onclick="searchData()">Search</button>
                <div id="data-results"></div>
            </div>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Processing...</p>
        </div>

        <div class="results" id="main-results" style="display: none;">
            <h3>Results</h3>
            <div id="results-content"></div>
        </div>
    </div>

    <script>
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadTables();
            getSyncStatus();
        });

        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }

        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }

        function showResults(content) {
            document.getElementById('results-content').innerHTML = content;
            document.getElementById('main-results').style.display = 'block';
        }

        function showStatus(elementId, message, type = 'info') {
            const element = document.getElementById(elementId);
            element.innerHTML = `<div class="status ${type}">${message}</div>`;
        }

        async function syncData() {
            showLoading();
            try {
                const response = await fetch('/api/sync', { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    showStatus('sync-status', data.message, 'success');
                } else {
                    showStatus('sync-status', `Error: ${data.error}`, 'error');
                }
            } catch (error) {
                showStatus('sync-status', `Error: ${error.message}`, 'error');
            }
            hideLoading();
        }

        async function getSyncStatus() {
            try {
                const response = await fetch('/api/sync/status');
                const data = await response.json();
                
                if (data.success) {
                    let statusHtml = '<h4>Database Status:</h4><table class="table">';
                    statusHtml += '<tr><th>Table</th><th>Records</th><th>Columns</th></tr>';
                    
                    for (const [table, info] of Object.entries(data.status.tables)) {
                        statusHtml += `<tr><td>${table}</td><td>${info.row_count}</td><td>${info.columns}</td></tr>`;
                    }
                    statusHtml += '</table>';
                    
                    showStatus('sync-status', statusHtml, 'info');
                }
            } catch (error) {
                showStatus('sync-status', `Status check failed: ${error.message}`, 'error');
            }
        }

        async function runAnalysis() {
            const analysisType = document.getElementById('analysis-type').value;
            showLoading();
            
            try {
                const response = await fetch(`/api/analyze/${analysisType}`);
                const data = await response.json();
                
                if (data.success) {
                    let resultsHtml = `<h4>${analysisType.toUpperCase()} Analysis Results:</h4>`;
                    resultsHtml += `<pre>${JSON.stringify(data.insights, null, 2)}</pre>`;
                    showResults(resultsHtml);
                    showStatus('analysis-results', 'Analysis completed successfully!', 'success');
                } else {
                    showStatus('analysis-results', `Error: ${data.error}`, 'error');
                }
            } catch (error) {
                showStatus('analysis-results', `Error: ${error.message}`, 'error');
            }
            hideLoading();
        }

        async function generateReport() {
            const reportType = document.getElementById('report-type').value;
            showLoading();
            
            try {
                const response = await fetch(`/api/report/${reportType}?save=true`);
                const data = await response.json();
                
                if (data.success) {
                    let resultsHtml = `<h4>${reportType.toUpperCase()} Report Generated:</h4>`;
                    if (data.result.saved_to) {
                        resultsHtml += `<p><strong>Saved to:</strong> ${data.result.saved_to}</p>`;
                    }
                    resultsHtml += `<div style="max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px;">`;
                    resultsHtml += data.result.content.replace(/\\n/g, '<br>');
                    resultsHtml += `</div>`;
                    showResults(resultsHtml);
                    showStatus('report-results', 'Report generated successfully!', 'success');
                } else {
                    showStatus('report-results', `Error: ${data.error}`, 'error');
                }
            } catch (error) {
                showStatus('report-results', `Error: ${error.message}`, 'error');
            }
            hideLoading();
        }

        async function loadTables() {
            try {
                const response = await fetch('/api/tables');
                const data = await response.json();
                
                if (data.success) {
                    const select = document.getElementById('table-select');
                    select.innerHTML = '<option value="">Select Table...</option>';
                    
                    for (const table of Object.keys(data.tables)) {
                        const option = document.createElement('option');
                        option.value = table;
                        option.textContent = `${table} (${data.tables[table].row_count} records)`;
                        select.appendChild(option);
                    }
                }
            } catch (error) {
                console.error('Failed to load tables:', error);
            }
        }

        async function loadTableData() {
            const table = document.getElementById('table-select').value;
            if (!table) return;
            
            showLoading();
            try {
                const response = await fetch(`/api/data/${table}?per_page=20`);
                const data = await response.json();
                
                if (data.success && data.data.length > 0) {
                    let resultsHtml = `<h4>Data from ${table}:</h4>`;
                    resultsHtml += '<table class="table"><tr>';
                    
                    // Headers
                    for (const key of Object.keys(data.data[0])) {
                        resultsHtml += `<th>${key}</th>`;
                    }
                    resultsHtml += '</tr>';
                    
                    // Data rows
                    for (const row of data.data.slice(0, 10)) {
                        resultsHtml += '<tr>';
                        for (const value of Object.values(row)) {
                            resultsHtml += `<td>${value || 'N/A'}</td>`;
                        }
                        resultsHtml += '</tr>';
                    }
                    resultsHtml += '</table>';
                    resultsHtml += `<p>Showing 10 of ${data.pagination.total} records</p>`;
                    
                    showResults(resultsHtml);
                } else {
                    showResults('<p>No data found</p>');
                }
            } catch (error) {
                showResults(`<p>Error loading data: ${error.message}</p>`);
            }
            hideLoading();
        }

        async function searchData() {
            const query = document.getElementById('search-query').value.trim();
            if (!query) return;
            
            showLoading();
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                
                if (data.success) {
                    let resultsHtml = `<h4>Search Results for "${query}":</h4>`;
                    
                    if (Object.keys(data.results).length === 0) {
                        resultsHtml += '<p>No results found</p>';
                    } else {
                        for (const [table, rows] of Object.entries(data.results)) {
                            resultsHtml += `<h5>${table} (${rows.length} results):</h5>`;
                            resultsHtml += '<table class="table"><tr>';
                            
                            if (rows.length > 0) {
                                for (const key of Object.keys(rows[0])) {
                                    resultsHtml += `<th>${key}</th>`;
                                }
                                resultsHtml += '</tr>';
                                
                                for (const row of rows.slice(0, 5)) {
                                    resultsHtml += '<tr>';
                                    for (const value of Object.values(row)) {
                                        resultsHtml += `<td>${value || 'N/A'}</td>`;
                                    }
                                    resultsHtml += '</tr>';
                                }
                            }
                            resultsHtml += '</table>';
                        }
                    }
                    
                    showResults(resultsHtml);
                } else {
                    showResults(`<p>Search failed: ${data.error}</p>`);
                }
            } catch (error) {
                showResults(`<p>Search error: ${error.message}</p>`);
            }
            hideLoading();
        }

        async function clearCache() {
            showLoading();
            try {
                const response = await fetch('/api/cache/clear');
                const data = await response.json();
                
                if (data.success) {
                    showStatus('sync-status', data.message, 'success');
                } else {
                    showStatus('sync-status', `Error: ${data.error}`, 'error');
                }
            } catch (error) {
                showStatus('sync-status', `Error: ${error.message}`, 'error');
            }
            hideLoading();
        }
    </script>
</body>
</html>
    '''

if __name__ == '__main__':
    # Initialize database on startup
    db_manager.initialize_database()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)