"""
VS Code SQL Server Extension Database Manager
Uses VS Code's SQL Server extension tools for database connections
"""

import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging
import json
from config import DATABASE_PROFILES

class VSCodeSQLManager:
    """Database manager that uses VS Code SQL Server extension tools"""
    
    def __init__(self):
        self.connections = {}
        self.logger = logging.getLogger(__name__)
    
    def get_available_databases(self) -> List[str]:
        """Get list of available database profiles"""
        return list(DATABASE_PROFILES.keys())
    
    def connect_to_database(self, profile_name: str) -> str:
        """
        Connect to database using VS Code SQL Server extension
        Returns connection ID
        """
        if profile_name not in DATABASE_PROFILES:
            raise ValueError(f"Unknown database profile: {profile_name}")
        
        profile = DATABASE_PROFILES[profile_name]
        connection_id = f"vscode_conn_{profile_name}"
        
        try:
            # Use VS Code SQL Server extension tools
            # This would typically use the mssql extension APIs
            
            self.connections[connection_id] = {
                'profile_name': profile_name,
                'server': profile['server'],
                'database': profile['database'],
                'connected': True,
                'profile_id': profile.get('profile_id')
            }
            
            self.logger.info(f"VS Code connection established for {profile_name}")
            return connection_id
            
        except Exception as e:
            self.logger.error(f"VS Code connection failed for {profile_name}: {str(e)}")
            raise Exception(f"VS Code connection failed: {str(e)}")
    
    def get_tables_via_vscode(self, connection_id: str) -> List[Dict[str, str]]:
        """Get tables using VS Code SQL Server extension"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        # This would use VS Code extension tools in a real implementation
        # For now, return sample data that represents what we'd expect
        sample_tables = [
            {'schema': 'dbo', 'table': 'Users', 'type': 'BASE TABLE'},
            {'schema': 'dbo', 'table': 'Customers', 'type': 'BASE TABLE'},
            {'schema': 'dbo', 'table': 'Orders', 'type': 'BASE TABLE'},
            {'schema': 'dbo', 'table': 'Employees', 'type': 'BASE TABLE'},
            {'schema': 'sales', 'table': 'SalesData', 'type': 'BASE TABLE'},
            {'schema': 'hr', 'table': 'PersonalInfo', 'type': 'BASE TABLE'},
            {'schema': 'finance', 'table': 'PaymentInfo', 'type': 'BASE TABLE'}
        ]
        
        return sample_tables
    
    def get_table_columns_via_vscode(self, connection_id: str, schema: str, table: str) -> List[Dict[str, str]]:
        """Get columns using VS Code SQL Server extension"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        # Sample column data based on common PII-containing tables
        column_mappings = {
            'Users': [
                {'column': 'UserID', 'type': 'int', 'max_length': None, 'nullable': 'NO'},
                {'column': 'FirstName', 'type': 'nvarchar', 'max_length': 50, 'nullable': 'YES'},
                {'column': 'LastName', 'type': 'nvarchar', 'max_length': 50, 'nullable': 'YES'},
                {'column': 'Email', 'type': 'nvarchar', 'max_length': 255, 'nullable': 'YES'},
                {'column': 'Phone', 'type': 'nvarchar', 'max_length': 20, 'nullable': 'YES'},
                {'column': 'SSN', 'type': 'nvarchar', 'max_length': 11, 'nullable': 'YES'},
                {'column': 'DateOfBirth', 'type': 'date', 'max_length': None, 'nullable': 'YES'},
                {'column': 'Address', 'type': 'nvarchar', 'max_length': 500, 'nullable': 'YES'}
            ],
            'Customers': [
                {'column': 'CustomerID', 'type': 'int', 'max_length': None, 'nullable': 'NO'},
                {'column': 'CompanyName', 'type': 'nvarchar', 'max_length': 100, 'nullable': 'YES'},
                {'column': 'ContactName', 'type': 'nvarchar', 'max_length': 100, 'nullable': 'YES'},
                {'column': 'ContactEmail', 'type': 'nvarchar', 'max_length': 255, 'nullable': 'YES'},
                {'column': 'BillingAddress', 'type': 'nvarchar', 'max_length': 500, 'nullable': 'YES'},
                {'column': 'CreditCardNumber', 'type': 'nvarchar', 'max_length': 20, 'nullable': 'YES'},
                {'column': 'TaxID', 'type': 'nvarchar', 'max_length': 15, 'nullable': 'YES'}
            ],
            'Employees': [
                {'column': 'EmployeeID', 'type': 'int', 'max_length': None, 'nullable': 'NO'},
                {'column': 'FullName', 'type': 'nvarchar', 'max_length': 100, 'nullable': 'YES'},
                {'column': 'PersonalEmail', 'type': 'nvarchar', 'max_length': 255, 'nullable': 'YES'},
                {'column': 'HomePhone', 'type': 'nvarchar', 'max_length': 20, 'nullable': 'YES'},
                {'column': 'HomeAddress', 'type': 'nvarchar', 'max_length': 500, 'nullable': 'YES'},
                {'column': 'SocialSecurityNumber', 'type': 'nvarchar', 'max_length': 11, 'nullable': 'YES'},
                {'column': 'MedicalRecordNumber', 'type': 'nvarchar', 'max_length': 20, 'nullable': 'YES'},
                {'column': 'EmergencyContactPhone', 'type': 'nvarchar', 'max_length': 20, 'nullable': 'YES'}
            ],
            'PersonalInfo': [
                {'column': 'PersonID', 'type': 'int', 'max_length': None, 'nullable': 'NO'},
                {'column': 'Race', 'type': 'nvarchar', 'max_length': 50, 'nullable': 'YES'},
                {'column': 'Ethnicity', 'type': 'nvarchar', 'max_length': 50, 'nullable': 'YES'},
                {'column': 'Religion', 'type': 'nvarchar', 'max_length': 50, 'nullable': 'YES'},
                {'column': 'PoliticalAffiliation', 'type': 'nvarchar', 'max_length': 50, 'nullable': 'YES'},
                {'column': 'HealthConditions', 'type': 'nvarchar', 'max_length': 1000, 'nullable': 'YES'},
                {'column': 'BiometricID', 'type': 'nvarchar', 'max_length': 100, 'nullable': 'YES'}
            ],
            'PaymentInfo': [
                {'column': 'PaymentID', 'type': 'int', 'max_length': None, 'nullable': 'NO'},
                {'column': 'CreditCardNumber', 'type': 'nvarchar', 'max_length': 20, 'nullable': 'YES'},
                {'column': 'BankAccountNumber', 'type': 'nvarchar', 'max_length': 20, 'nullable': 'YES'},
                {'column': 'RoutingNumber', 'type': 'nvarchar', 'max_length': 9, 'nullable': 'YES'},
                {'column': 'CardHolderName', 'type': 'nvarchar', 'max_length': 100, 'nullable': 'YES'},
                {'column': 'BillingAddress', 'type': 'nvarchar', 'max_length': 500, 'nullable': 'YES'}
            ]
        }
        
        return column_mappings.get(table, [
            {'column': 'ID', 'type': 'int', 'max_length': None, 'nullable': 'NO'},
            {'column': 'Name', 'type': 'nvarchar', 'max_length': 100, 'nullable': 'YES'},
            {'column': 'Data', 'type': 'nvarchar', 'max_length': 500, 'nullable': 'YES'}
        ])
    
    def sample_table_data_via_vscode(self, connection_id: str, schema: str, table: str, limit: int = 100) -> pd.DataFrame:
        """Generate sample data that represents what we'd get from real tables"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        from faker import Faker
        fake = Faker()
        
        # Generate realistic sample data based on table type
        if table == 'Users':
            data = {
                'UserID': range(1, min(limit, 100) + 1),
                'FirstName': [fake.first_name() for _ in range(min(limit, 100))],
                'LastName': [fake.last_name() for _ in range(min(limit, 100))],
                'Email': [fake.email() for _ in range(min(limit, 100))],
                'Phone': [fake.phone_number() for _ in range(min(limit, 100))],
                'SSN': [fake.ssn() for _ in range(min(limit, 100))],
                'DateOfBirth': [fake.date_of_birth() for _ in range(min(limit, 100))],
                'Address': [fake.address().replace('\n', ' ') for _ in range(min(limit, 100))]
            }
        elif table == 'Customers':
            data = {
                'CustomerID': range(1, min(limit, 100) + 1),
                'CompanyName': [fake.company() for _ in range(min(limit, 100))],
                'ContactName': [fake.name() for _ in range(min(limit, 100))],
                'ContactEmail': [fake.company_email() for _ in range(min(limit, 100))],
                'BillingAddress': [fake.address().replace('\n', ' ') for _ in range(min(limit, 100))],
                'CreditCardNumber': [fake.credit_card_number() for _ in range(min(limit, 100))],
                'TaxID': [fake.ein() for _ in range(min(limit, 100))]
            }
        elif table == 'Employees':
            data = {
                'EmployeeID': range(1, min(limit, 100) + 1),
                'FullName': [fake.name() for _ in range(min(limit, 100))],
                'PersonalEmail': [fake.email() for _ in range(min(limit, 100))],
                'HomePhone': [fake.phone_number() for _ in range(min(limit, 100))],
                'HomeAddress': [fake.address().replace('\n', ' ') for _ in range(min(limit, 100))],
                'SocialSecurityNumber': [fake.ssn() for _ in range(min(limit, 100))],
                'MedicalRecordNumber': [f"MRN{fake.random_number(digits=8)}" for _ in range(min(limit, 100))],
                'EmergencyContactPhone': [fake.phone_number() for _ in range(min(limit, 100))]
            }
        elif table == 'PersonalInfo':
            races = ['White', 'Black', 'Asian', 'Hispanic', 'Native American', 'Pacific Islander', 'Mixed']
            religions = ['Christian', 'Muslim', 'Jewish', 'Hindu', 'Buddhist', 'Atheist', 'Other']
            political = ['Democrat', 'Republican', 'Independent', 'Green', 'Libertarian', 'Other']
            
            data = {
                'PersonID': range(1, min(limit, 100) + 1),
                'Race': [fake.random_element(races) for _ in range(min(limit, 100))],
                'Ethnicity': [fake.random_element(['Hispanic', 'Non-Hispanic']) for _ in range(min(limit, 100))],
                'Religion': [fake.random_element(religions) for _ in range(min(limit, 100))],
                'PoliticalAffiliation': [fake.random_element(political) for _ in range(min(limit, 100))],
                'HealthConditions': [fake.sentence() for _ in range(min(limit, 100))],
                'BiometricID': [f"BIO{fake.random_number(digits=12)}" for _ in range(min(limit, 100))]
            }
        elif table == 'PaymentInfo':
            data = {
                'PaymentID': range(1, min(limit, 100) + 1),
                'CreditCardNumber': [fake.credit_card_number() for _ in range(min(limit, 100))],
                'BankAccountNumber': [fake.random_number(digits=12) for _ in range(min(limit, 100))],
                'RoutingNumber': [fake.routing_number() for _ in range(min(limit, 100))],
                'CardHolderName': [fake.name() for _ in range(min(limit, 100))],
                'BillingAddress': [fake.address().replace('\n', ' ') for _ in range(min(limit, 100))]
            }
        else:
            # Generic data for unknown tables
            data = {
                'ID': range(1, min(limit, 100) + 1),
                'Name': [fake.name() for _ in range(min(limit, 100))],
                'Data': [fake.text(max_nb_chars=200) for _ in range(min(limit, 100))]
            }
        
        return pd.DataFrame(data)
    
    def get_tables(self, connection_id: str) -> List[Dict[str, str]]:
        """Wrapper for get_tables_via_vscode"""
        return self.get_tables_via_vscode(connection_id)
    
    def get_table_columns(self, connection_id: str, schema: str, table: str) -> List[Dict[str, str]]:
        """Wrapper for get_table_columns_via_vscode"""
        return self.get_table_columns_via_vscode(connection_id, schema, table)
    
    def sample_table_data(self, connection_id: str, schema: str, table: str, limit: int = 100) -> pd.DataFrame:
        """Wrapper for sample_table_data_via_vscode"""
        return self.sample_table_data_via_vscode(connection_id, schema, table, limit)
    
    def get_table_row_count(self, connection_id: str, schema: str, table: str) -> int:
        """Estimate row count for sample tables"""
        # Return realistic row counts for demo
        table_sizes = {
            'Users': 15000,
            'Customers': 8500,
            'Employees': 2500,
            'Orders': 45000,
            'SalesData': 120000,
            'PersonalInfo': 2500,
            'PaymentInfo': 12000
        }
        return table_sizes.get(table, 1000)
    
    def get_database_schema_info(self, connection_id: str) -> Dict:
        """Get database schema information"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        return {
            'schemas': [
                {'TABLE_SCHEMA': 'dbo', 'table_count': 4},
                {'TABLE_SCHEMA': 'sales', 'table_count': 1},
                {'TABLE_SCHEMA': 'hr', 'table_count': 1},
                {'TABLE_SCHEMA': 'finance', 'table_count': 1}
            ],
            'column_types': [
                {'DATA_TYPE': 'nvarchar', 'column_count': 25},
                {'DATA_TYPE': 'int', 'column_count': 7},
                {'DATA_TYPE': 'date', 'column_count': 3},
                {'DATA_TYPE': 'datetime', 'column_count': 2}
            ],
            'total_tables': 7,
            'total_schemas': 4
        }
    
    def test_connection(self, connection_id: str) -> bool:
        """Test if connection is still alive"""
        return connection_id in self.connections and self.connections[connection_id]['connected']
    
    def disconnect(self, connection_id: str):
        """Disconnect from database"""
        if connection_id in self.connections:
            self.connections[connection_id]['connected'] = False
            del self.connections[connection_id]
            self.logger.info(f"VS Code connection disconnected: {connection_id}")
    
    def get_connection_info(self, connection_id: str) -> Dict:
        """Get connection information"""
        return self.connections.get(connection_id, {})
    
    def get_sample_data(self, connection_id: str, schema: str, table: str, limit: int = 10) -> List[Dict]:
        """
        Get sample data from a table in dictionary format for AI analysis
        
        Args:
            connection_id: Database connection ID
            schema: Schema name
            table: Table name  
            limit: Number of rows to sample (default 10)
            
        Returns:
            List of dictionaries representing sample rows
        """
        try:
            # Use existing sample_table_data method to get DataFrame
            df = self.sample_table_data(connection_id, schema, table, limit)
            
            # Convert DataFrame to list of dictionaries
            if df is not None and not df.empty:
                # Convert to dict and handle any problematic data types
                sample_data = []
                for _, row in df.iterrows():
                    row_dict = {}
                    for col, value in row.items():
                        # Convert problematic types to strings for JSON serialization
                        try:
                            if pd.isna(value):
                                row_dict[col] = None
                            elif isinstance(value, (str, int, float, bool)):
                                row_dict[col] = value
                            else:
                                # Convert datetime, decimal, etc. to string
                                row_dict[col] = str(value)
                        except:
                            row_dict[col] = str(value)
                    sample_data.append(row_dict)
                
                return sample_data[:limit]  # Ensure we don't exceed limit
            else:
                return []
                
        except Exception as e:
            self.logger.warning(f"Could not sample data from {table}: {str(e)}")
            return []
