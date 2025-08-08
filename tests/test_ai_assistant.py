#!/usr/bin/env python3
"""
Test script for the enhanced AI Assistant with batch processing and compliance features
"""

import asyncio
import logging
from ai_assistant import AIAssistant, TableRecommendation

# Set up logging
logging.basicConfig(level=logging.INFO)

def create_sample_tables():
    """Create sample table data to test batch processing"""
    tables = []
    
    # High-risk tables with names and sensitive data
    high_risk_tables = [
        {
            'table': 'Person', 
            'schema': 'Person',
            'columns': [
                {'column': 'PersonID'}, {'column': 'FirstName'}, {'column': 'LastName'}, 
                {'column': 'MiddleName'}, {'column': 'EmailAddress'}, {'column': 'PhoneNumber'}
            ],
            'row_count': 19972
        },
        {
            'table': 'Employee', 
            'schema': 'HumanResources',
            'columns': [
                {'column': 'EmployeeID'}, {'column': 'FirstName'}, {'column': 'LastName'},
                {'column': 'SSN'}, {'column': 'BirthDate'}, {'column': 'HireDate'}
            ],
            'row_count': 290
        },
        {
            'table': 'Patient', 
            'schema': 'Healthcare',
            'columns': [
                {'column': 'PatientID'}, {'column': 'FullName'}, {'column': 'DateOfBirth'},
                {'column': 'MedicalRecordNumber'}, {'column': 'Diagnosis'}, {'column': 'Treatment'}
            ],
            'row_count': 15000
        },
        {
            'table': 'Customer', 
            'schema': 'Sales',
            'columns': [
                {'column': 'CustomerID'}, {'column': 'CustomerName'}, {'column': 'EmailAddress'},
                {'column': 'CreditCardNumber'}, {'column': 'BillingAddress'}
            ],
            'row_count': 5432
        }
    ]
    
    # Medium-risk tables
    medium_risk_tables = [
        {
            'table': 'Address', 
            'schema': 'Person',
            'columns': [
                {'column': 'AddressID'}, {'column': 'AddressLine1'}, {'column': 'City'},
                {'column': 'StateProvince'}, {'column': 'PostalCode'}, {'column': 'CountryRegion'}
            ],
            'row_count': 19614
        },
        {
            'table': 'EmailAddress', 
            'schema': 'Person',
            'columns': [
                {'column': 'BusinessEntityID'}, {'column': 'EmailAddressID'}, 
                {'column': 'EmailAddress'}, {'column': 'ModifiedDate'}
            ],
            'row_count': 19972
        }
    ]
    
    # Low-risk reference tables
    low_risk_tables = [
        {
            'table': 'ProductCategory', 
            'schema': 'Production',
            'columns': [
                {'column': 'ProductCategoryID'}, {'column': 'Name'}, {'column': 'ModifiedDate'}
            ],
            'row_count': 4
        },
        {
            'table': 'Currency', 
            'schema': 'Sales',
            'columns': [
                {'column': 'CurrencyCode'}, {'column': 'Name'}, {'column': 'ModifiedDate'}
            ],
            'row_count': 105
        }
    ]
    
    # Skip dbo schema tables (should be filtered out)
    dbo_tables = [
        {
            'table': 'SystemLog', 
            'schema': 'dbo',
            'columns': [
                {'column': 'LogID'}, {'column': 'Message'}, {'column': 'Timestamp'}
            ],
            'row_count': 100000
        }
    ]
    
    # Combine all tables
    tables.extend(high_risk_tables)
    tables.extend(medium_risk_tables)
    tables.extend(low_risk_tables)
    tables.extend(dbo_tables)
    
    # Add many more tables to test batch processing
    for i in range(50):
        tables.append({
            'table': f'TestTable{i}',
            'schema': 'Test',
            'columns': [
                {'column': 'ID'}, {'column': 'Data'}, {'column': 'CreatedDate'}
            ],
            'row_count': 100
        })
    
    return tables

async def test_ai_assistant():
    """Test the enhanced AI Assistant"""
    print("🔍 Testing Enhanced AI Assistant with Batch Processing and Compliance Features")
    print("=" * 80)
    
    # Initialize AI Assistant
    assistant = AIAssistant()
    
    if not assistant.is_available():
        print("❌ AI Assistant not available (no API key configured)")
        print("✅ Testing fallback rule-based analysis...")
    else:
        print("✅ AI Assistant initialized successfully")
    
    # Create sample data
    sample_tables = create_sample_tables()
    print(f"📊 Created {len(sample_tables)} sample tables for testing")
    
    # Test table analysis
    print("\n🔬 Analyzing tables for PII...")
    try:
        recommendations = await assistant.analyze_tables_for_pii(sample_tables)
        
        print(f"\n📋 Found {len(recommendations)} table recommendations:")
        print("-" * 80)
        
        for i, rec in enumerate(recommendations[:10], 1):  # Show top 10
            compliance_info = ""
            if "Compliance:" in rec.reasoning:
                compliance_part = rec.reasoning.split("Compliance:")[-1].strip()
                compliance_info = f"\n   📜 Compliance: {compliance_part}"
            
            print(f"{i:2d}. {rec.schema}.{rec.table_name}")
            print(f"    🎯 Priority: {rec.priority} (Confidence: {rec.confidence_score:.2f})")
            print(f"    🔍 PII Types: {', '.join(rec.estimated_pii_types)}")
            print(f"    💭 Reasoning: {rec.reasoning.split('|')[0].strip()}{compliance_info}")
            print()
        
        # Show statistics
        high_priority = [r for r in recommendations if r.priority == 'HIGH']
        medium_priority = [r for r in recommendations if r.priority == 'MEDIUM']
        low_priority = [r for r in recommendations if r.priority == 'LOW']
        
        print(f"📊 Priority Summary:")
        print(f"   🔴 HIGH Priority: {len(high_priority)} tables")
        print(f"   🟡 MEDIUM Priority: {len(medium_priority)} tables") 
        print(f"   🟢 LOW Priority: {len(low_priority)} tables")
        
        # Check for critical name tables
        name_tables = [r for r in recommendations if any('NAME' in pii_type for pii_type in r.estimated_pii_types)]
        print(f"   👤 Tables with Name Columns: {len(name_tables)} (requiring encryption)")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_pii_decision():
    """Test PII action decision"""
    print("\n🤖 Testing PII Action Suggestions...")
    print("-" * 50)
    
    assistant = AIAssistant()
    
    # Test different PII types
    test_cases = [
        ('FULL_NAME', 'John D***', {'table': 'Person', 'column': 'FullName'}),
        ('SSN', '123-**-****', {'table': 'Employee', 'column': 'SSN'}),
        ('EMAIL', 'john.****@example.com', {'table': 'Customer', 'column': 'Email'}),
        ('PHONE', '555-***-****', {'table': 'Contact', 'column': 'Phone'})
    ]
    
    for pii_type, sample, context in test_cases:
        try:
            decision = await assistant.suggest_pii_action(pii_type, sample, context)
            print(f"📝 {pii_type}: {decision.action} (confidence: {decision.confidence:.2f})")
            print(f"   💭 Reasoning: {decision.reasoning}")
            if decision.encryption_key_hint:
                print(f"   🔐 Key hint: {decision.encryption_key_hint}")
            print()
        except Exception as e:
            print(f"❌ Error testing {pii_type}: {str(e)}")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_ai_assistant())
    asyncio.run(test_pii_decision())
    
    print("✅ AI Assistant testing completed!")
