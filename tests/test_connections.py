"""
Database Connection Test Script
Tests connections to all configured databases with fallback options
"""

from real_database_manager import RealDatabaseManager
from vscode_sql_manager import VSCodeSQLManager
from database_manager import DatabaseManager
from config import DATABASE_PROFILES
import logging

def test_database_connections():
    """Test database connections with multiple connection types"""
    print("🔗 Testing Database Connections")
    print("=" * 40)
    
    # Test different connection types
    managers_to_test = [
        ("ODBC Direct Connection", RealDatabaseManager),
        ("VS Code SQL Extension", VSCodeSQLManager),  
        ("Demo Mode", DatabaseManager)
    ]
    
    successful_manager = None
    
    for manager_name, manager_class in managers_to_test:
        print(f"\n🧪 Testing {manager_name}...")
        
        try:
            db_manager = manager_class()
            results = {}
            
            for db_name in DATABASE_PROFILES.keys():
                print(f"  📊 Testing {db_name}...")
                
                try:
                    # Test connection
                    connection_id = db_manager.connect_to_database(db_name)
                    print(f"    ✅ Connected successfully")
                    
                    # Test getting tables
                    tables = db_manager.get_tables(connection_id)
                    print(f"    📋 Found {len(tables)} tables")
                    
                    # Test getting schema info if available
                    try:
                        schema_info = db_manager.get_database_schema_info(connection_id)
                        if schema_info:
                            print(f"    🏗️ Schemas: {schema_info.get('total_schemas', 0)}")
                            print(f"    📊 Total tables: {schema_info.get('total_tables', 0)}")
                    except AttributeError:
                        print(f"    ℹ️ Schema info not available for this connection type")
                    
                    # Test a few tables for column information
                    if tables:
                        sample_tables = tables[:2]  # Test first 2 tables
                        for table in sample_tables:
                            try:
                                columns = db_manager.get_table_columns(
                                    connection_id, table['schema'], table['table']
                                )
                                print(f"      • {table['schema']}.{table['table']}: {len(columns)} columns")
                            except Exception as e:
                                print(f"      ⚠️ Could not get columns for {table['schema']}.{table['table']}: {str(e)}")
                    
                    # Test sample data
                    if tables:
                        try:
                            first_table = tables[0]
                            sample_data = db_manager.sample_table_data(
                                connection_id, first_table['schema'], first_table['table'], 5
                            )
                            print(f"      📄 Sample data: {len(sample_data)} rows, {len(sample_data.columns)} columns")
                        except Exception as e:
                            print(f"      ⚠️ Could not get sample data: {str(e)}")
                    
                    # Disconnect
                    db_manager.disconnect(connection_id)
                    print(f"    🔌 Disconnected")
                    
                    results[db_name] = {
                        'status': 'SUCCESS',
                        'tables': len(tables),
                        'schemas': schema_info.get('total_schemas', 0) if isinstance(schema_info, dict) else 0
                    }
                    
                except Exception as e:
                    print(f"    ❌ Connection failed: {str(e)}")
                    results[db_name] = {
                        'status': 'FAILED',
                        'error': str(e)
                    }
            
            # Summary for this manager
            successful = [db for db, result in results.items() if result['status'] == 'SUCCESS']
            failed = [db for db, result in results.items() if result['status'] == 'FAILED']
            
            print(f"\n  📈 {manager_name} Summary:")
            print(f"  ✅ Successful: {len(successful)}/{len(results)}")
            
            if len(successful) == len(results):
                print(f"  🎉 All connections successful with {manager_name}!")
                successful_manager = manager_name
                return results, successful_manager
            elif successful:
                print(f"  ⚠️ Partial success with {manager_name}")
                for db in successful:
                    result = results[db]
                    print(f"    • {db}: {result['tables']} tables, {result['schemas']} schemas")
                
                for db in failed:
                    print(f"    ❌ {db}: {results[db]['error']}")
            else:
                print(f"  ❌ No successful connections with {manager_name}")
                
        except Exception as e:
            print(f"  💥 {manager_name} initialization failed: {str(e)}")
            continue
    
    return {}, None

def check_system_requirements():
    """Check system requirements for database connections"""
    print("\n🔍 System Requirements Check")
    print("-" * 30)
    
    # Check pyodbc
    try:
        import pyodbc
        drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
        print("✅ pyodbc installed")
        if drivers:
            print(f"✅ SQL Server drivers found: {len(drivers)}")
            for driver in drivers:
                print(f"   • {driver}")
        else:
            print("⚠️ No SQL Server ODBC drivers found")
            print("   Install Microsoft ODBC Driver for SQL Server")
    except ImportError:
        print("❌ pyodbc not installed")
    
    # Check pandas
    try:
        import pandas
        print("✅ pandas installed")
    except ImportError:
        print("❌ pandas not installed")
    
    # Check other requirements
    try:
        import streamlit
        print("✅ streamlit installed")
    except ImportError:
        print("❌ streamlit not installed")

if __name__ == "__main__":
    try:
        # Check system requirements first
        check_system_requirements()
        
        # Test connections
        results, successful_manager = test_database_connections()
        
        # Final summary
        print(f"\n🎯 Final Summary")
        print("=" * 20)
        
        if successful_manager:
            print(f"✅ Recommended connection method: {successful_manager}")
            print(f"🚀 Ready to run: streamlit run app.py")
        else:
            print("⚠️ No connection methods were fully successful")
            print("💡 Recommendations:")
            print("   1. Install Microsoft ODBC Driver for SQL Server")
            print("   2. Use VS Code SQL Server extension")
            print("   3. Try Demo Mode for testing")
        
        print(f"\n📝 Installation Guide:")
        print("   ODBC Driver: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
        print("   VS Code Extension: Search 'SQL Server (mssql)' in extensions")
            
    except Exception as e:
        print(f"❌ Test script failed: {str(e)}")
        exit(1)
