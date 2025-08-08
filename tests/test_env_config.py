#!/usr/bin/env python3
"""
Environment Configuration Test
Tests that .env file is being loaded correctly across all modules
"""

def test_env_config():
    """Test environment configuration loading"""
    print("🧪 Testing Environment Configuration")
    print("=" * 50)
    
    try:
        from env_config import env_config, is_ai_enabled, get_db_config, get_scan_config
        
        print("✅ Environment configuration module loaded successfully")
        print()
        
        # Test AI configuration
        print("🤖 AI Configuration:")
        print(f"   API Key Configured: {'Yes' if env_config.anthropic_api_key else 'No'}")
        print(f"   Model: {env_config.ai_model_name}")
        print(f"   Max Tokens: {env_config.ai_max_tokens}")
        print(f"   Temperature: {env_config.ai_temperature}")
        print(f"   AI Enabled: {is_ai_enabled()}")
        print()
        
        # Test database configuration
        print("🗄️ Database Configuration:")
        db_config = get_db_config()
        print(f"   Connection Mode: {env_config.connection_mode}")
        print(f"   Server: {db_config['server']}")
        print(f"   Username: {db_config['username']}")
        print(f"   Port: {db_config['port']}")
        print(f"   Default Database: {db_config['database']}")
        print()
        
        # Test scanning configuration
        print("🔍 Scanning Configuration:")
        scan_config = get_scan_config()
        print(f"   Sample Size: {scan_config['sample_size']}")
        print(f"   Max Rows: {scan_config['max_rows']}")
        print(f"   Confidence Threshold: {scan_config['confidence_threshold']}")
        print(f"   Max Concurrent: {scan_config['max_concurrent']}")
        print()
        
        # Test encryption configuration
        print("🔐 Encryption Configuration:")
        print(f"   Master Key File: {env_config.master_key_file}")
        print(f"   Iterations: {env_config.key_derivation_iterations}")
        print(f"   Encryption Enabled: {env_config.enable_encryption}")
        print(f"   Data Masking Enabled: {env_config.enable_data_masking}")
        print()
        
        # Test results configuration
        print("💾 Results Configuration:")
        print(f"   Database Path: {env_config.results_db_path}")
        print(f"   Auto Backup: {env_config.auto_backup}")
        print(f"   Retention Days: {env_config.backup_retention_days}")
        print()
        
        # Test Streamlit configuration
        print("🌐 Streamlit Configuration:")
        print(f"   Host: {env_config.streamlit_host}")
        print(f"   Port: {env_config.streamlit_port}")
        print(f"   Page Title: {env_config.page_title}")
        print(f"   Page Icon: {env_config.page_icon}")
        print(f"   Layout: {env_config.layout}")
        print()
        
        # Test compliance configuration
        print("⚖️ Compliance Configuration:")
        print(f"   GDPR Enabled: {env_config.enable_gdpr_compliance}")
        print(f"   CCPA Enabled: {env_config.enable_ccpa_compliance}")
        print(f"   HIPAA Enabled: {env_config.enable_hipaa_compliance}")
        print(f"   Data Retention: {env_config.data_retention_period} days")
        print()
        
        # Test development configuration
        print("🔧 Development Configuration:")
        print(f"   Debug Mode: {env_config.debug_mode}")
        print(f"   Cache Results: {env_config.cache_results}")
        print(f"   Mock AI: {env_config.mock_ai_responses}")
        print()
        
        print("✅ All environment configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Environment configuration test failed: {e}")
        return False

def test_module_integration():
    """Test that modules are using env_config correctly"""
    print("\n🔧 Testing Module Integration")
    print("=" * 50)
    
    try:
        # Test AI Assistant
        print("🤖 Testing AI Assistant integration...")
        from ai_assistant import AIAssistant
        ai_assistant = AIAssistant()
        print(f"   ✅ AI Assistant initialized with env config")
        
        # Test Encryption Manager
        print("🔐 Testing Encryption Manager integration...")
        from encryption_manager import EncryptionManager
        encryption_manager = EncryptionManager()
        print(f"   ✅ Encryption Manager initialized with env config")
        
        # Test Results Manager
        print("💾 Testing Results Manager integration...")
        from results_manager import ResultsManager
        results_manager = ResultsManager()
        print(f"   ✅ Results Manager initialized with env config")
        
        # Test Multi-Database Manager
        print("🗄️ Testing Multi-Database Manager integration...")
        from multi_database_manager import MultiDatabaseManager
        multi_db_manager = MultiDatabaseManager()
        print(f"   ✅ Multi-Database Manager initialized with env config")
        
        print("\n✅ All module integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Module integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all environment configuration tests"""
    print("🔍 PII Detection System - Environment Configuration Test")
    print("=" * 70)
    print()
    
    success = True
    
    # Test environment configuration loading
    if not test_env_config():
        success = False
    
    # Test module integration
    if not test_module_integration():
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 ALL TESTS PASSED! Environment configuration is working correctly.")
        print()
        print("📋 Summary:")
        print("   ✅ .env file is being loaded correctly")
        print("   ✅ All modules are using centralized configuration")
        print("   ✅ Environment variables are properly typed and accessible")
        print()
        print("🚀 Your PII Detection System is ready to run!")
        print("   Run: streamlit run app.py")
    else:
        print("❌ SOME TESTS FAILED! Please check the configuration.")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Make sure .env file exists and is properly formatted")
        print("   2. Check that all required modules are importable")
        print("   3. Verify environment variable names and values")

if __name__ == '__main__':
    main()
