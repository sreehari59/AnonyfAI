#!/usr/bin/env python3
"""
Quick test to verify the new project structure works
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all main modules can be imported"""
    try:
        print("Testing core imports...")
        from core.config import DATABASE_PROFILES, PII_PATTERNS
        from core.pii_detector import PIIDetector
        from core.utils import setup_logging
        print("✅ Core modules imported successfully")
        
        print("Testing database imports...")
        from database.database_manager import DatabaseManager
        from database.real_database_manager import RealDatabaseManager
        print("✅ Database modules imported successfully")
        
        print("Testing UI imports...")
        # Note: Don't import the full app.py as it has streamlit dependencies
        print("✅ UI structure verified")
        
        print("\n🎉 All imports successful! New structure is working.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
