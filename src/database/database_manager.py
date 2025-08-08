"""
Database Manager for PII Detection
Handles SQL Server connections and database operations
"""

import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging
from config import DATABASE_PROFILES

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.connections = {}
        self.logger = logging.getLogger(__name__)
    
    def get_available_databases(self) -> List[str]:
        """Get list of available database profiles"""
        return list(DATABASE_PROFILES.keys())
    
    def connect_to_database(self, profile_name: str) -> str:
        """
        Connect to database using profile name
        Returns connection ID
        """
        if profile_name not in DATABASE_PROFILES:
            raise ValueError(f"Unknown database profile: {profile_name}")
        
        profile = DATABASE_PROFILES[profile_name]
        
        # This would use the mssql_connect function from VS Code extension
        # For now, we'll simulate the connection
        connection_id = f"conn_{profile_name}"
        self.connections[connection_id] = {
            'profile_name': profile_name,
            'server': profile['server'],
            'database': profile['database'],
            'connected': True
        }
        
        return connection_id
    
    def get_tables(self, connection_id: str) -> List[Dict[str, str]]:
        """Get list of tables in the connected database"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        # This would use the mssql_list_tables function
        # For now, return some sample tables
        sample_tables = [
            {'schema': 'dbo', 'table': 'Users'},
            {'schema': 'dbo', 'table': 'Customers'},
            {'schema': 'dbo', 'table': 'Orders'},
            {'schema': 'hr', 'table': 'Employees'},
            {'schema': 'sales', 'table': 'SalesPersons'}
        ]
        return sample_tables
    
    def get_table_columns(self, connection_id: str, schema: str, table: str) -> List[Dict[str, str]]:
        """Get columns for a specific table"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        # Sample column information
        sample_columns = {
            'Users': [
                {'column': 'UserID', 'type': 'int'},
                {'column': 'FirstName', 'type': 'varchar'},
                {'column': 'LastName', 'type': 'varchar'},
                {'column': 'Email', 'type': 'varchar'},
                {'column': 'Phone', 'type': 'varchar'},
                {'column': 'SSN', 'type': 'varchar'}
            ],
            'Customers': [
                {'column': 'CustomerID', 'type': 'int'},
                {'column': 'CompanyName', 'type': 'varchar'},
                {'column': 'ContactEmail', 'type': 'varchar'},
                {'column': 'BillingAddress', 'type': 'text'},
                {'column': 'CreditCardNumber', 'type': 'varchar'}
            ],
            'Employees': [
                {'column': 'EmployeeID', 'type': 'int'},
                {'column': 'FullName', 'type': 'varchar'},
                {'column': 'DateOfBirth', 'type': 'date'},
                {'column': 'PersonalEmail', 'type': 'varchar'},
                {'column': 'HomePhone', 'type': 'varchar'},
                {'column': 'Address', 'type': 'text'}
            ]
        }
        
        return sample_columns.get(table, [
            {'column': 'ID', 'type': 'int'},
            {'column': 'Name', 'type': 'varchar'},
            {'column': 'Data', 'type': 'text'}
        ])
    
    def sample_table_data(self, connection_id: str, schema: str, table: str, limit: int = 100) -> pd.DataFrame:
        """Get sample data from a table"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        # For prototype, return sample data
        from faker import Faker
        fake = Faker()
        
        if table == 'Users':
            data = {
                'UserID': range(1, limit + 1),
                'FirstName': [fake.first_name() for _ in range(limit)],
                'LastName': [fake.last_name() for _ in range(limit)],
                'Email': [fake.email() for _ in range(limit)],
                'Phone': [fake.phone_number() for _ in range(limit)],
                'SSN': [fake.ssn() for _ in range(limit)]
            }
        elif table == 'Customers':
            data = {
                'CustomerID': range(1, limit + 1),
                'CompanyName': [fake.company() for _ in range(limit)],
                'ContactEmail': [fake.email() for _ in range(limit)],
                'BillingAddress': [fake.address() for _ in range(limit)],
                'CreditCardNumber': [fake.credit_card_number() for _ in range(limit)]
            }
        elif table == 'Employees':
            data = {
                'EmployeeID': range(1, limit + 1),
                'FullName': [fake.name() for _ in range(limit)],
                'DateOfBirth': [fake.date_of_birth() for _ in range(limit)],
                'PersonalEmail': [fake.email() for _ in range(limit)],
                'HomePhone': [fake.phone_number() for _ in range(limit)],
                'Address': [fake.address() for _ in range(limit)]
            }
        else:
            data = {
                'ID': range(1, limit + 1),
                'Name': [fake.name() for _ in range(limit)],
                'Data': [fake.text() for _ in range(limit)]
            }
        
        return pd.DataFrame(data)
    
    def execute_query(self, connection_id: str, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        # For prototype, simulate query execution
        # In real implementation, this would use mssql_run_query
        self.logger.info(f"Executing query: {query}")
        
        # Return empty DataFrame for now
        return pd.DataFrame()
    
    def disconnect(self, connection_id: str):
        """Disconnect from database"""
        if connection_id in self.connections:
            self.connections[connection_id]['connected'] = False
            del self.connections[connection_id]
    
    def get_connection_info(self, connection_id: str) -> Dict:
        """Get connection information"""
        return self.connections.get(connection_id, {})
