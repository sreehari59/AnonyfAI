"""
Enhanced Database Manager for PII Detection
Handles real SQL Server connections and database operations
"""

import pandas as pd
import pyodbc
from typing import List, Dict, Tuple, Optional
import logging
import warnings
import asyncio
import concurrent.futures
from functools import partial
from config import DATABASE_PROFILES

# Suppress pandas SQLAlchemy warnings for pyodbc connections
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy connectable', category=UserWarning)
warnings.filterwarnings('ignore', message='Could not create connection from', category=UserWarning) 
warnings.filterwarnings('ignore', category=UserWarning, module='pandas.io.sql')
warnings.filterwarnings('ignore', message='.*dialect name.*', category=UserWarning)

class RealDatabaseManager:
    """Enhanced database manager that connects to real SQL Server databases"""
    
    def __init__(self):
        self.connections = {}
        self.logger = logging.getLogger(__name__)
    
    def get_available_databases(self) -> List[str]:
        """Get list of available database profiles"""
        return list(DATABASE_PROFILES.keys())
    
    def connect_to_database(self, profile_name: str) -> str:
        """
        Connect to database using profile name and credentials
        Returns connection ID
        """
        if profile_name not in DATABASE_PROFILES:
            raise ValueError(f"Unknown database profile: {profile_name}")
        
        profile = DATABASE_PROFILES[profile_name]
        connection_id = f"conn_{profile_name}"
        
        try:
            # Try multiple ODBC drivers in order of preference
            drivers_to_try = [
                "ODBC Driver 18 for SQL Server",
                "ODBC Driver 17 for SQL Server", 
                "ODBC Driver 13 for SQL Server",
                "SQL Server Native Client 11.0",
                "SQL Server"
            ]
            
            connection_string = None
            last_error = None
            
            for driver in drivers_to_try:
                try:
                    connection_string = (
                        f"DRIVER={{{driver}}};"
                        f"SERVER={profile['server']},{profile['port']};"
                        f"DATABASE={profile['database']};"
                        f"UID={profile['username']};"
                        f"PWD={profile['password']};"
                        f"Encrypt=yes;"
                        f"TrustServerCertificate=yes;"  # Allow self-signed certs
                        f"Connection Timeout=30;"
                    )
                    
                    # Test the connection string
                    test_connection = pyodbc.connect(connection_string)
                    test_connection.close()
                    break  # If successful, use this driver
                    
                except pyodbc.Error as e:
                    last_error = e
                    self.logger.debug(f"Driver {driver} failed: {str(e)}")
                    continue
            
            if not connection_string:
                # If all ODBC drivers fail, provide helpful error message
                available_drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
                raise Exception(
                    f"No suitable SQL Server ODBC driver found. "
                    f"Available drivers: {available_drivers}. "
                    f"Last error: {str(last_error)}"
                )
            
            # Establish connection
            connection = pyodbc.connect(connection_string)
            
            self.connections[connection_id] = {
                'connection': connection,
                'profile_name': profile_name,
                'server': profile['server'],
                'database': profile['database'],
                'connected': True
            }
            
            self.logger.info(f"Successfully connected to {profile_name}")
            return connection_id
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {profile_name}: {str(e)}")
            raise Exception(f"Connection failed: {str(e)}")
    
    def get_tables(self, connection_id: str) -> List[Dict[str, str]]:
        """Get list of tables in the connected database with improved connection handling"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")

        connection = self.connections[connection_id]['connection']

        try:
            # Ensure any previous operations are complete and close any open cursors
            try:
                connection.commit()
            except:
                pass

            # Create a new cursor for this operation
            cursor = connection.cursor()
            
            try:
                query = """
                SELECT 
                    TABLE_SCHEMA as schema_name,
                    TABLE_NAME as table_name,
                    TABLE_TYPE as table_type
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME
                """

                cursor.execute(query)

                tables = []
                for row in cursor.fetchall():
                    tables.append({
                        'schema': row.schema_name,
                        'table': row.table_name,
                        'type': row.table_type
                    })

                return tables
                
            finally:
                # Always close the cursor to free up the connection
                cursor.close()

        except Exception as e:
            self.logger.error(f"Error getting tables: {str(e)}")
            raise Exception(f"Failed to get tables: {str(e)}")
    
    def get_table_columns(self, connection_id: str, schema: str, table: str) -> List[Dict[str, str]]:
        """Get columns for a specific table with improved connection management"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        connection = self.connections[connection_id]['connection']
        
        try:
            # Ensure any previous operations are complete
            try:
                connection.commit()
            except:
                pass
            
            query = """
            SELECT 
                COLUMN_NAME as column_name,
                DATA_TYPE as data_type,
                CHARACTER_MAXIMUM_LENGTH as max_length,
                IS_NULLABLE as is_nullable,
                COLUMN_DEFAULT as default_value
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
            """
            
            cursor = connection.cursor()
            
            try:
                cursor.execute(query, (schema, table))
                
                columns = []
                for row in cursor.fetchall():
                    columns.append({
                        'column': row.column_name,
                        'type': row.data_type,
                        'max_length': row.max_length,
                        'nullable': row.is_nullable,
                        'default': row.default_value
                    })
                
                return columns
                
            finally:
                # Always close the cursor
                cursor.close()
            
        except Exception as e:
            self.logger.error(f"Error getting columns: {str(e)}")
            raise Exception(f"Failed to get columns: {str(e)}")
    
    def sample_table_data(self, connection_id: str, schema: str, table: str, limit: int = 100) -> pd.DataFrame:
        """Get sample data from a table with enhanced error handling and connection management"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        connection = self.connections[connection_id]['connection']
        
        try:
            # Ensure any previous operations are complete
            try:
                connection.commit()
            except:
                pass
            
            # Use cursor-first approach to avoid pandas ODBC issues
            cursor = connection.cursor()
            
            try:
                # Get column info first to identify problematic types
                cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                ORDER BY ORDINAL_POSITION
                """, (schema, table))
                
                column_info = cursor.fetchall()
                safe_columns = []
                
                for row in column_info:
                    col_name = row[0]
                    data_type = row[1]
                    max_length = row[2]
                    
                    # Handle problematic SQL Server data types more comprehensively
                    data_type_upper = data_type.upper()
                    if data_type_upper in ['IMAGE', 'TEXT', 'NTEXT', 'XML', 'GEOGRAPHY', 'GEOMETRY', 'HIERARCHYID', 'SQL_VARIANT', 'TIMESTAMP', 'ROWVERSION']:
                        # Convert to NVARCHAR for display
                        safe_columns.append(f"CAST([{col_name}] AS NVARCHAR(500)) AS [{col_name}]")
                    elif data_type_upper in ['VARBINARY', 'BINARY']:
                        # Convert binary to hex string for display
                        safe_columns.append(f"CONVERT(VARCHAR(MAX), [{col_name}], 2) AS [{col_name}]")
                    elif data_type_upper in ['UNIQUEIDENTIFIER']:
                        # Convert GUID to string
                        safe_columns.append(f"CAST([{col_name}] AS VARCHAR(50)) AS [{col_name}]")
                    elif data_type_upper in ['MONEY', 'SMALLMONEY']:
                        # Convert money types to decimal for compatibility
                        safe_columns.append(f"CAST([{col_name}] AS DECIMAL(19,4)) AS [{col_name}]")
                    elif data_type_upper in ['DATETIMEOFFSET']:
                        # Convert to standard datetime
                        safe_columns.append(f"CAST([{col_name}] AS DATETIME2) AS [{col_name}]")
                    else:
                        # Use column as-is for standard types
                        safe_columns.append(f"[{col_name}]")
                
                if safe_columns:
                    # Build WHERE clause to exclude rows where all columns are NULL
                    # Create NOT NULL conditions for each original column
                    not_null_conditions = []
                    for row in column_info:
                        col_name = row[0]
                        not_null_conditions.append(f"[{col_name}] IS NOT NULL")
                    
                    # Use OR to get rows where at least one column is not null
                    where_clause = f"WHERE ({' OR '.join(not_null_conditions)})" if not_null_conditions else ""
                    
                    safe_query = f"""
                    SELECT TOP {limit} {', '.join(safe_columns)}
                    FROM [{schema}].[{table}]
                    {where_clause}
                    """
                    
                    self.logger.debug(f"Executing safe query for {schema}.{table}")
                    cursor.execute(safe_query)
                    columns = [column[0] for column in cursor.description]
                    
                    # Fetch rows with robust data type handling
                    rows = []
                    try:
                        for row in cursor.fetchall():
                            converted_row = []
                            for i, value in enumerate(row):
                                try:
                                    if value is None:
                                        converted_row.append(None)
                                    elif isinstance(value, (str, int, float, bool)):
                                        converted_row.append(value)
                                    elif isinstance(value, (bytes, bytearray)):
                                        # Convert binary data to readable string
                                        try:
                                            converted_row.append(value.decode('utf-8', errors='ignore'))
                                        except:
                                            converted_row.append(f"<binary:{len(value)}bytes>")
                                    else:
                                        # Convert other types (datetime, decimal, etc.) to string
                                        converted_row.append(str(value))
                                except Exception as conv_error:
                                    # Fallback for any conversion issues
                                    converted_row.append(f"<error:{type(value).__name__}>")
                            rows.append(converted_row)
                    except Exception as fetch_error:
                        self.logger.warning(f"Error fetching rows from {schema}.{table}: {fetch_error}")
                        rows = []
                    
                    # Create DataFrame
                    if rows:
                        df = pd.DataFrame(rows, columns=columns)
                        self.logger.info(f"Successfully sampled {len(rows)} rows from {schema}.{table}")
                    else:
                        df = pd.DataFrame(columns=columns)
                        self.logger.warning(f"No rows returned from {schema}.{table}")
                    
                    return df
                else:
                    raise Exception("No safe columns found to sample")
                    
            finally:
                cursor.close()
                
        except Exception as main_error:
            self.logger.error(f"Error sampling data from {schema}.{table}: {main_error}")
            
            # Return informative error DataFrame with more specific guidance
            error_msg = str(main_error)
            if "ODBC SQL type -151" in error_msg:
                reason = "SQL Server proprietary data type not supported by ODBC driver"
                suggestion = "Table contains unsupported data types (possibly hierarchyid, geometry, or xml)"
            elif "Connection is busy" in error_msg:
                reason = "Database connection is busy with another operation"
                suggestion = "Try refreshing the connection or running the operation again"
            else:
                reason = error_msg
                suggestion = "Check database permissions and table accessibility"
            
            return pd.DataFrame({
                'Error': [f"Could not sample data from {schema}.{table}"],
                'Reason': [reason],
                'Suggestion': [suggestion],
                'Table': [f"{schema}.{table}"],
                'Status': ['Failed - Continuing with next table']
            })
    
    async def sample_table_data_async(self, connection_id: str, schema: str, table: str, limit: int = 100) -> pd.DataFrame:
        """
        Async version of sample_table_data for better performance when sampling multiple tables
        
        Args:
            connection_id: Database connection ID
            schema: Schema name
            table: Table name
            limit: Number of rows to sample (default 100)
            
        Returns:
            DataFrame with sample data or error information
        """
        # Use ThreadPoolExecutor to run the synchronous database operation in a separate thread
        loop = asyncio.get_event_loop()
        
        # Create a partial function with the arguments bound
        sync_function = partial(self.sample_table_data, connection_id, schema, table, limit)
        
        # Run the synchronous function in a thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            try:
                result = await loop.run_in_executor(executor, sync_function)
                return result
            except Exception as e:
                self.logger.error(f"Async error sampling data from {schema}.{table}: {e}")
                return pd.DataFrame({
                    'Error': [f"Async sampling failed for {schema}.{table}"],
                    'Reason': [str(e)],
                    'Suggestion': ["Check database connection and table accessibility"],
                    'Table': [f"{schema}.{table}"],
                    'Status': ['Failed - Async operation error']
                })
    
    async def sample_multiple_tables_async(self, connection_id: str, tables: List[Dict[str, str]], limit: int = 100) -> Dict[str, pd.DataFrame]:
        """
        Sample multiple tables concurrently using async operations
        
        Args:
            connection_id: Database connection ID
            tables: List of dicts with 'schema' and 'table' keys
            limit: Number of rows to sample per table
            
        Returns:
            Dictionary mapping "schema.table" to DataFrame results
        """
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        # Create async tasks for each table
        tasks = []
        table_keys = []
        
        for table_info in tables:
            schema = table_info.get('schema', '')
            table = table_info.get('table', '')
            if schema and table:
                task = self.sample_table_data_async(connection_id, schema, table, limit)
                tasks.append(task)
                table_keys.append(f"{schema}.{table}")
        
        if not tasks:
            return {}
        
        # Execute all tasks concurrently
        self.logger.info(f"Starting async sampling of {len(tasks)} tables...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle any exceptions
        output = {}
        for i, (table_key, result) in enumerate(zip(table_keys, results)):
            if isinstance(result, Exception):
                self.logger.error(f"Exception sampling {table_key}: {result}")
                output[table_key] = pd.DataFrame({
                    'Error': [f"Exception during async sampling of {table_key}"],
                    'Reason': [str(result)],
                    'Suggestion': ["Check database connection and retry"],
                    'Table': [table_key],
                    'Status': ['Failed - Exception occurred']
                })
            else:
                output[table_key] = result
                if not result.empty and 'Error' not in result.columns:
                    self.logger.info(f"Successfully sampled {len(result)} rows from {table_key}")
        
        return output
    
    async def get_sample_data_async(self, connection_id: str, schema: str, table: str, limit: int = 10) -> List[Dict]:
        """
        Async version of get_sample_data that returns data in dictionary format for AI analysis
        
        Args:
            connection_id: Database connection ID
            schema: Schema name
            table: Table name  
            limit: Number of rows to sample (default 10)
            
        Returns:
            List of dictionaries representing sample rows
        """
        try:
            # Use async version to get DataFrame
            df = await self.sample_table_data_async(connection_id, schema, table, limit)
            
            # Convert DataFrame to list of dictionaries
            if df is not None and not df.empty and 'Error' not in df.columns:
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
            self.logger.warning(f"Could not async sample data from {table}: {str(e)}")
            return []
    
    def sample_multiple_tables_sync(self, connection_id: str, tables: List[Dict[str, str]], limit: int = 100) -> Dict[str, pd.DataFrame]:
        """
        Synchronous wrapper for async multiple table sampling - for use in Streamlit
        
        Args:
            connection_id: Database connection ID
            tables: List of dicts with 'schema' and 'table' keys
            limit: Number of rows to sample per table
            
        Returns:
            Dictionary mapping "schema.table" to DataFrame results
        """
        try:
            # Create new event loop for this operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run the async function
                result = loop.run_until_complete(
                    self.sample_multiple_tables_async(connection_id, tables, limit)
                )
                return result
            finally:
                # Clean up the loop
                loop.close()
                
        except Exception as e:
            self.logger.error(f"Error in sync wrapper for multiple table sampling: {e}")
            # Fallback to sequential processing
            return self._fallback_sequential_sampling(connection_id, tables, limit)
    
    def _fallback_sequential_sampling(self, connection_id: str, tables: List[Dict[str, str]], limit: int = 100) -> Dict[str, pd.DataFrame]:
        """Fallback method for sequential table sampling if async fails"""
        results = {}
        for table_info in tables:
            schema = table_info.get('schema', '')
            table = table_info.get('table', '')
            if schema and table:
                table_key = f"{schema}.{table}"
                try:
                    df = self.sample_table_data(connection_id, schema, table, limit)
                    results[table_key] = df
                except Exception as e:
                    self.logger.error(f"Error sampling {table_key}: {e}")
                    results[table_key] = pd.DataFrame({
                        'Error': [f"Sequential sampling failed for {table_key}"],
                        'Reason': [str(e)],
                        'Table': [table_key],
                        'Status': ['Failed - Fallback error']
                    })
        return results
    
    def get_table_row_count(self, connection_id: str, schema: str, table: str) -> int:
        """Get total row count for a table"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        connection = self.connections[connection_id]['connection']
        
        try:
            query = f"SELECT COUNT(*) as row_count FROM [{schema}].[{table}]"
            
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            
            return result.row_count if result else 0
            
        except Exception as e:
            self.logger.error(f"Error getting row count: {str(e)}")
            return 0
    
    def execute_query(self, connection_id: str, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        connection = self.connections[connection_id]['connection']
        
        try:
            df = pd.read_sql(query, connection)
            return df
            
        except Exception as e:
            self.logger.error(f"Error executing query: {str(e)}")
            raise Exception(f"Failed to execute query: {str(e)}")
    
    def get_database_schema_info(self, connection_id: str) -> Dict:
        """Get comprehensive database schema information"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        connection = self.connections[connection_id]['connection']
        
        try:
            # Get table counts by schema
            schema_query = """
            SELECT 
                TABLE_SCHEMA,
                COUNT(*) as table_count
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            GROUP BY TABLE_SCHEMA
            ORDER BY TABLE_SCHEMA
            """
            
            # Get column statistics
            column_query = """
            SELECT 
                DATA_TYPE,
                COUNT(*) as column_count
            FROM INFORMATION_SCHEMA.COLUMNS
            GROUP BY DATA_TYPE
            ORDER BY COUNT(*) DESC
            """
            
            schema_df = pd.read_sql(schema_query, connection)
            column_df = pd.read_sql(column_query, connection)
            
            return {
                'schemas': schema_df.to_dict('records'),
                'column_types': column_df.to_dict('records'),
                'total_tables': schema_df['table_count'].sum(),
                'total_schemas': len(schema_df)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting schema info: {str(e)}")
            return {}
    
    def search_columns_by_name(self, connection_id: str, pattern: str) -> List[Dict]:
        """Search for columns containing specific patterns"""
        if connection_id not in self.connections:
            raise ValueError(f"Invalid connection ID: {connection_id}")
        
        connection = self.connections[connection_id]['connection']
        
        try:
            query = """
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                COLUMN_NAME,
                DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE LOWER(COLUMN_NAME) LIKE LOWER(?)
            ORDER BY TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME
            """
            
            cursor = connection.cursor()
            cursor.execute(query, (f'%{pattern}%',))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'schema': row.TABLE_SCHEMA,
                    'table': row.TABLE_NAME,
                    'column': row.COLUMN_NAME,
                    'type': row.DATA_TYPE
                })
            
            cursor.close()
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching columns: {str(e)}")
            return []
    
    def disconnect(self, connection_id: str):
        """Disconnect from database"""
        if connection_id in self.connections:
            try:
                self.connections[connection_id]['connection'].close()
                self.connections[connection_id]['connected'] = False
                del self.connections[connection_id]
                self.logger.info(f"Disconnected from {connection_id}")
            except Exception as e:
                self.logger.error(f"Error disconnecting: {str(e)}")
    
    def get_connection_info(self, connection_id: str) -> Dict:
        """Get connection information"""
        if connection_id in self.connections:
            conn_info = self.connections[connection_id].copy()
            # Don't return the actual connection object
            conn_info.pop('connection', None)
            return conn_info
        return {}
    
    def test_connection(self, connection_id: str) -> bool:
        """Test if connection is still alive"""
        if connection_id not in self.connections:
            return False
        
        try:
            connection = self.connections[connection_id]['connection']
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except:
            return False
    
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
