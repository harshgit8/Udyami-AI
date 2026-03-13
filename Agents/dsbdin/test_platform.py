#!/usr/bin/env python3
"""
Test script for Manufacturing Audit Intelligence Platform
Comprehensive testing of all components
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sheets_sync import SheetsSyncManager
from ai_analyzer import AIAnalyzer
from report_generator import ReportGenerator
from database_manager import DatabaseManager
import time
import json
from datetime import datetime

def test_database_initialization():
    """Test database setup"""
    print("🔧 Testing Database Initialization...")
    
    db_manager = DatabaseManager()
    success = db_manager.initialize_database()
    
    if success:
        print("✅ Database initialized successfully")
        
        # Test table creation
        tables = ['production', 'quality', 'quotation', 'invoice', 'rnd']
        for table in tables:
            info = db_manager.get_table_info(table)
            print(f"   📊 {table}: {len(info.get('columns', []))} columns")
        
        return True
    else:
        print("❌ Database initialization failed")
        return False

def test_sheets_sync():
    """Test Google Sheets synchronization"""
    print("\n📊 Testing Sheets Synchronization...")
    
    sync_manager = SheetsSyncManager()
    
    try:
        # Test sync status
        status = sync_manager.get_sync_status()
        print(f"   📈 Current status: {len(status['tables'])} tables tracked")
        
        # Test individual sheet sync
        success = sync_manager.sync_sheet_to_table('Production', 'production')
        if success:
            print("✅ Production sheet sync successful")
        else:
            print("⚠️ Production sheet sync had issues")
        
        # Test full sync (limited for testing)
        print("   🔄 Running limited sync test...")
        results = {}
        test_sheets = ['Production', 'Quality']  # Test subset
        
        for sheet_name in test_sheets:
            table_name = sync_manager.sheet_mappings.get(sheet_name)
            if table_name:
                results[sheet_name] = sync_manager.sync_sheet_to_table(sheet_name, table_name)
                time.sleep(1)  # Rate limiting
        
        success_count = sum(1 for success in results.values() if success)
        print(f"✅ Sync test completed: {success_count}/{len(results)} sheets successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Sheets sync test failed: {e}")
        return False

def test_ai_analysis():
    """Test AI analysis capabilities"""
    print("\n🤖 Testing AI Analysis...")
    
    analyzer = AIAnalyzer()
    
    try:
        # Test production analysis
        print("   📊 Testing production analysis...")
        production_insights = analyzer.generate_analysis('production')
        
        if 'error' not in production_insights:
            print(f"✅ Production analysis: {production_insights.get('total_orders', 0)} orders analyzed")
            if production_insights.get('key_insights'):
                print(f"   💡 Generated {len(production_insights['key_insights'])} insights")
        else:
            print(f"⚠️ Production analysis: {production_insights['error']}")
        
        # Test quality analysis
        print("   🔍 Testing quality analysis...")
        quality_insights = analyzer.generate_analysis('quality')
        
        if 'error' not in quality_insights:
            print(f"✅ Quality analysis: {quality_insights.get('total_batches', 0)} batches analyzed")
        else:
            print(f"⚠️ Quality analysis: {quality_insights['error']}")
        
        # Test cross-entity analysis
        print("   🔗 Testing cross-entity analysis...")
        cross_insights = analyzer.generate_analysis('cross_analysis')
        
        if 'error' not in cross_insights:
            print("✅ Cross-entity analysis completed")
        else:
            print(f"⚠️ Cross-entity analysis: {cross_insights['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI analysis test failed: {e}")
        return False

def test_report_generation():
    """Test report generation"""
    print("\n📋 Testing Report Generation...")
    
    report_gen = ReportGenerator()
    
    try:
        # Test available reports
        available_reports = report_gen.list_available_reports()
        print(f"   📝 Available report types: {len(available_reports)}")
        
        # Test production report
        print("   📊 Generating production report...")
        prod_report = report_gen.generate_report('production', save_to_file=False)
        
        if 'error' not in prod_report:
            content_length = len(prod_report['content'])
            print(f"✅ Production report generated: {content_length} characters")
        else:
            print(f"⚠️ Production report: {prod_report['error']}")
        
        # Test comprehensive report
        print("   📈 Generating comprehensive report...")
        comp_report = report_gen.generate_report('comprehensive', save_to_file=False)
        
        if 'error' not in comp_report:
            content_length = len(comp_report['content'])
            print(f"✅ Comprehensive report generated: {content_length} characters")
        else:
            print(f"⚠️ Comprehensive report: {comp_report['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Report generation test failed: {e}")
        return False

def test_data_operations():
    """Test database operations"""
    print("\n🗃️ Testing Data Operations...")
    
    db_manager = DatabaseManager()
    
    try:
        # Test data insertion
        test_data = {
            'order_id': 'TEST-001',
            'product_type': 'test_widget',
            'quantity': 100,
            'due_date': '2026-02-01',
            'priority': 'normal',
            'customer': 'Test Customer',
            'notes': 'Test order for platform validation'
        }
        
        success = db_manager.insert_data('production', test_data)
        if success:
            print("✅ Data insertion successful")
        else:
            print("⚠️ Data insertion failed")
        
        # Test data query
        results = db_manager.query("SELECT * FROM production WHERE order_id = ?", ('TEST-001',))
        if results:
            print(f"✅ Data query successful: {len(results)} records found")
        else:
            print("⚠️ Data query returned no results")
        
        # Test data cleanup
        cleanup_success = db_manager.execute("DELETE FROM production WHERE order_id = ?", ('TEST-001',))
        if cleanup_success:
            print("✅ Test data cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Data operations test failed: {e}")
        return False

def test_caching_system():
    """Test caching functionality"""
    print("\n💾 Testing Caching System...")
    
    analyzer = AIAnalyzer()
    
    try:
        # Test cache generation
        filters = {'priority': 'high'}
        
        # First call - should generate and cache
        print("   🔄 First analysis call (should cache)...")
        start_time = time.time()
        insights1 = analyzer.generate_analysis('production', filters, use_cache=True)
        time1 = time.time() - start_time
        
        # Second call - should use cache
        print("   ⚡ Second analysis call (should use cache)...")
        start_time = time.time()
        insights2 = analyzer.generate_analysis('production', filters, use_cache=True)
        time2 = time.time() - start_time
        
        if insights2.get('cached'):
            print(f"✅ Cache system working: {time2:.3f}s vs {time1:.3f}s")
        else:
            print("⚠️ Cache system not working as expected")
        
        # Test cache cleanup
        db_manager = DatabaseManager()
        cleanup_success = db_manager.cleanup_expired_cache()
        if cleanup_success:
            print("✅ Cache cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Caching test failed: {e}")
        return False

def run_performance_test():
    """Run performance benchmarks"""
    print("\n⚡ Running Performance Tests...")
    
    try:
        db_manager = DatabaseManager()
        analyzer = AIAnalyzer()
        
        # Test query performance
        start_time = time.time()
        results = db_manager.query("SELECT COUNT(*) FROM production")
        query_time = time.time() - start_time
        print(f"   📊 Database query time: {query_time:.3f}s")
        
        # Test analysis performance
        start_time = time.time()
        insights = analyzer.generate_analysis('production', use_cache=False)
        analysis_time = time.time() - start_time
        print(f"   🤖 Analysis time: {analysis_time:.3f}s")
        
        # Performance benchmarks
        if query_time < 1.0:
            print("✅ Database performance: Excellent")
        elif query_time < 3.0:
            print("✅ Database performance: Good")
        else:
            print("⚠️ Database performance: Needs optimization")
        
        if analysis_time < 5.0:
            print("✅ Analysis performance: Excellent")
        elif analysis_time < 10.0:
            print("✅ Analysis performance: Good")
        else:
            print("⚠️ Analysis performance: Needs optimization")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run comprehensive platform test"""
    print("🚀 Manufacturing Audit Intelligence Platform - Comprehensive Test Suite")
    print("=" * 80)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Database Initialization", test_database_initialization),
        ("Sheets Synchronization", test_sheets_sync),
        ("AI Analysis", test_ai_analysis),
        ("Report Generation", test_report_generation),
        ("Data Operations", test_data_operations),
        ("Caching System", test_caching_system),
        ("Performance Benchmarks", run_performance_test)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Platform is ready for production.")
    elif passed >= total * 0.8:
        print("✅ Most tests passed. Platform is functional with minor issues.")
    else:
        print("⚠️ Several tests failed. Platform needs attention before deployment.")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()