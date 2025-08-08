"""
PII Detection Prototype Demo Script
Demonstrates the capabilities of the PII detection system
"""

import pandas as pd
from real_database_manager import RealDatabaseManager
from pii_detector import PIIDetector
from utils import setup_logging, format_risk_score
from config import DATABASE_PROFILES, PII_PATTERNS

def main():
    """Main demo function"""
    print("🔒 PII Detection Prototype Demo")
    print("=" * 50)
    
    # Setup logging
    logger = setup_logging()
    
    # Initialize components
    db_manager = RealDatabaseManager()
    pii_detector = PIIDetector()
    
    print("\n📋 Available Databases:")
    for db_name in db_manager.get_available_databases():
        print(f"  • {db_name}")
    
    print(f"\n🔍 PII Detection Patterns: {len(PII_PATTERNS)} patterns loaded")
    print("Regulatory Coverage:")
    regulations = set()
    for pattern in PII_PATTERNS.values():
        regulations.update(pattern.get('regulations', []))
    for reg in sorted(regulations):
        print(f"  • {reg}")
    
    # Demo pattern matching
    print("\n🧪 Pattern Matching Demo:")
    test_data = [
        "John Doe's SSN is 123-45-6789",
        "Contact him at john.doe@email.com",
        "Phone: (555) 123-4567",
        "Credit Card: 4532-1234-5678-9012",
        "Medical Record: MRN123456789"
    ]
    
    for test_text in test_data:
        matches = pii_detector.detect_pii_in_text(test_text)
        print(f"  Text: {test_text}")
        for match in matches:
            print(f"    → {match.pattern_type}: {match.confidence:.2f} confidence")
    
    print(f"\n✅ Demo completed successfully!")
    print("To run the full application: streamlit run app.py")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
