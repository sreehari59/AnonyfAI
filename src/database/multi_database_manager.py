"""
Multi-Database Manager
Handles simultaneous connections to multiple databases for comprehensive PII scanning
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
import time

from database_manager import DatabaseManager
from real_database_manager import RealDatabaseManager
from vscode_sql_manager import VSCodeSQLManager

@dataclass
class DatabaseConnection:
    name: str
    manager: Any
    connection_id: str
    status: str  # CONNECTED, DISCONNECTED, ERROR
    last_activity: datetime
    error_message: Optional[str] = None

@dataclass
class MultiDatabaseScanResult:
    database_name: str
    tables_scanned: int
    pii_instances_found: int
    scan_duration: float
    status: str  # COMPLETED, FAILED, PARTIAL
    error_message: Optional[str] = None
    table_results: List[Dict[str, Any]] = None

class MultiDatabaseManager:
    def __init__(self, use_real_data: bool = True):
        """Initialize multi-database manager"""
        self.logger = logging.getLogger(__name__)
        self.connections: Dict[str, DatabaseConnection] = {}
        self.use_real_data = use_real_data
        self.executor = ThreadPoolExecutor(max_workers=5)  # Limit concurrent connections
        
        # Initialize database managers based on mode
        if use_real_data:
            try:
                self.primary_manager = RealDatabaseManager()
                self.fallback_manager = VSCodeSQLManager()
            except Exception as e:
                self.logger.warning(f"Real database manager failed, using fallback: {e}")
                self.primary_manager = VSCodeSQLManager()
                self.fallback_manager = DatabaseManager()  # Demo mode as last resort
        else:
            self.primary_manager = DatabaseManager()  # Demo mode
            self.fallback_manager = None
    
    def get_available_databases(self) -> List[str]:
        """Get list of all available databases"""
        try:
            return self.primary_manager.get_available_databases()
        except Exception as e:
            self.logger.error(f"Failed to get available databases: {e}")
            if self.fallback_manager:
                return self.fallback_manager.get_available_databases()
            return []
    
    def connect_to_databases(self, database_names: List[str]) -> Dict[str, DatabaseConnection]:
        """
        Connect to multiple databases simultaneously
        
        Args:
            database_names: List of database names to connect to
        
        Returns:
            Dictionary mapping database names to connection info
        """
        self.logger.info(f"Connecting to {len(database_names)} databases: {database_names}")
        
        # Use thread pool to connect to databases in parallel
        future_to_db = {}
        for db_name in database_names:
            future = self.executor.submit(self._connect_single_database, db_name)
            future_to_db[future] = db_name
        
        # Collect results
        connections = {}
        for future in as_completed(future_to_db):
            db_name = future_to_db[future]
            try:
                connection = future.result(timeout=30)  # 30 second timeout per connection
                connections[db_name] = connection
                self.connections[db_name] = connection
                
                if connection.status == 'CONNECTED':
                    self.logger.info(f"Successfully connected to {db_name}")
                else:
                    self.logger.warning(f"Failed to connect to {db_name}: {connection.error_message}")
                    
            except Exception as e:
                self.logger.error(f"Connection to {db_name} failed with exception: {e}")
                connections[db_name] = DatabaseConnection(
                    name=db_name,
                    manager=None,
                    connection_id="",
                    status='ERROR',
                    last_activity=datetime.now(),
                    error_message=str(e)
                )
        
        successful_connections = sum(1 for conn in connections.values() if conn.status == 'CONNECTED')
        self.logger.info(f"Successfully connected to {successful_connections}/{len(database_names)} databases")
        
        return connections
    
    def _connect_single_database(self, db_name: str) -> DatabaseConnection:
        """Connect to a single database (used in thread pool)"""
        try:
            # Try primary manager first
            connection_id = self.primary_manager.connect_to_database(db_name)
            
            return DatabaseConnection(
                name=db_name,
                manager=self.primary_manager,
                connection_id=connection_id,
                status='CONNECTED',
                last_activity=datetime.now()
            )
            
        except Exception as e:
            self.logger.warning(f"Primary connection to {db_name} failed: {e}")
            
            # Try fallback manager if available
            if self.fallback_manager:
                try:
                    connection_id = self.fallback_manager.connect_to_database(db_name)
                    
                    return DatabaseConnection(
                        name=db_name,
                        manager=self.fallback_manager,
                        connection_id=connection_id,
                        status='CONNECTED',
                        last_activity=datetime.now()
                    )
                    
                except Exception as fallback_error:
                    self.logger.error(f"Fallback connection to {db_name} also failed: {fallback_error}")
            
            # Both attempts failed
            return DatabaseConnection(
                name=db_name,
                manager=None,
                connection_id="",
                status='ERROR',
                last_activity=datetime.now(),
                error_message=str(e)
            )
    
    def get_all_tables(self, connection_filter: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get tables from all connected databases
        
        Args:
            connection_filter: Optional list of database names to include
        
        Returns:
            Dictionary mapping database names to their table lists
        """
        all_tables = {}
        
        connections_to_check = self.connections
        if connection_filter:
            connections_to_check = {k: v for k, v in self.connections.items() if k in connection_filter}
        
        for db_name, connection in connections_to_check.items():
            if connection.status == 'CONNECTED' and connection.manager:
                try:
                    # Test connection before getting tables
                    if hasattr(connection.manager, 'test_connection'):
                        if not connection.manager.test_connection(connection.connection_id):
                            self.logger.warning(f"Connection test failed for {db_name}")
                            # Attempt to reconnect
                            try:
                                self.logger.info(f"Attempting to reconnect to {db_name}")
                                new_connection_id = connection.manager.connect_to_database(db_name)
                                connection.connection_id = new_connection_id
                                connection.status = 'CONNECTED'
                                connection.last_activity = datetime.now()
                                connection.error_message = None
                                self.logger.info(f"Successfully reconnected to {db_name}")
                            except Exception as reconnect_error:
                                self.logger.error(f"Reconnection to {db_name} failed: {reconnect_error}")
                                connection.status = 'DISCONNECTED'
                                connection.error_message = str(reconnect_error)
                                all_tables[db_name] = []
                                continue
                    
                    tables = connection.manager.get_tables(connection.connection_id)
                    if tables is None:
                        tables = []
                    
                    all_tables[db_name] = tables
                    connection.last_activity = datetime.now()
                    
                    self.logger.debug(f"Retrieved {len(tables)} tables from {db_name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to get tables from {db_name}: {e}")
                    connection.status = 'ERROR'
                    connection.error_message = str(e)
                    all_tables[db_name] = []
            else:
                self.logger.warning(f"Skipping {db_name} - not connected")
                all_tables[db_name] = []
        
        return all_tables
    
    def scan_databases_for_pii(self, 
                              database_selection: Optional[Dict[str, List[str]]] = None,
                              sample_size: int = 100,
                              confidence_threshold: float = 0.7) -> List[MultiDatabaseScanResult]:
        """
        Scan multiple databases for PII simultaneously
        
        Args:
            database_selection: Dict mapping database names to table lists (None = scan all)
            sample_size: Number of rows to sample per table
            confidence_threshold: Minimum confidence for PII detection
        
        Returns:
            List of scan results per database
        """
        if database_selection is None:
            # Scan all connected databases, but first refresh their connection status
            database_selection = {}
            for db_name, connection in self.connections.items():
                if connection.status == 'CONNECTED':
                    try:
                        # Test connection before getting tables
                        if hasattr(connection.manager, 'test_connection'):
                            if not connection.manager.test_connection(connection.connection_id):
                                self.logger.warning(f"Connection test failed for {db_name} during scan setup")
                                # Attempt to reconnect
                                try:
                                    self.logger.info(f"Attempting to reconnect to {db_name}")
                                    new_connection_id = connection.manager.connect_to_database(db_name)
                                    connection.connection_id = new_connection_id
                                    connection.status = 'CONNECTED'
                                    connection.last_activity = datetime.now()
                                    connection.error_message = None
                                    self.logger.info(f"Successfully reconnected to {db_name}")
                                except Exception as reconnect_error:
                                    self.logger.error(f"Reconnection to {db_name} failed: {reconnect_error}")
                                    connection.status = 'DISCONNECTED'
                                    continue
                        
                        tables = connection.manager.get_tables(connection.connection_id)
                        if tables:
                            database_selection[db_name] = [f"{t['schema']}.{t['table']}" for t in tables[:10]]  # Limit to first 10 tables
                        else:
                            database_selection[db_name] = []
                    except Exception as e:
                        self.logger.error(f"Failed to get tables for {db_name}: {e}")
                        database_selection[db_name] = []
                        
        # Filter out databases with no tables or failed connections
        database_selection = {k: v for k, v in database_selection.items() if v and k in self.connections and self.connections[k].status == 'CONNECTED'}
        
        self.logger.info(f"Starting PII scan across {len(database_selection)} databases")
        
        if not database_selection:
            self.logger.warning("No databases available for scanning - all connections may have failed")
            return []
        
        # Use thread pool to scan databases in parallel
        future_to_db = {}
        for db_name, table_list in database_selection.items():
            if db_name in self.connections and self.connections[db_name].status == 'CONNECTED':
                future = self.executor.submit(
                    self._scan_single_database,
                    db_name,
                    table_list,
                    sample_size,
                    confidence_threshold
                )
                future_to_db[future] = db_name
        
        # Collect results
        scan_results = []
        for future in as_completed(future_to_db):
            db_name = future_to_db[future]
            try:
                result = future.result(timeout=300)  # 5 minute timeout per database
                scan_results.append(result)
                
                self.logger.info(f"Completed PII scan for {db_name}: "
                               f"{result.tables_scanned} tables, {result.pii_instances_found} PII instances")
                
            except Exception as e:
                self.logger.error(f"PII scan failed for {db_name}: {e}")
                scan_results.append(MultiDatabaseScanResult(
                    database_name=db_name,
                    tables_scanned=0,
                    pii_instances_found=0,
                    scan_duration=0.0,
                    status='FAILED',
                    error_message=str(e)
                ))
        
        return scan_results
    
    def get_connection_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current status of all connections for debugging"""
        status_info = {}
        for db_name, connection in self.connections.items():
            # Test current connection status
            is_alive = False
            if connection.status == 'CONNECTED' and connection.manager and hasattr(connection.manager, 'test_connection'):
                try:
                    is_alive = connection.manager.test_connection(connection.connection_id)
                except Exception as e:
                    is_alive = False
                    
            status_info[db_name] = {
                'stored_status': connection.status,
                'actual_status': 'CONNECTED' if is_alive else 'DISCONNECTED',
                'last_activity': connection.last_activity.isoformat() if connection.last_activity else None,
                'error_message': connection.error_message,
                'manager_type': type(connection.manager).__name__ if connection.manager else None
            }
            
        return status_info
    
    def refresh_connections(self):
        """Refresh all database connections by testing and reconnecting if needed"""
        self.logger.info("Refreshing all database connections")
        
        for db_name, connection in self.connections.items():
            if connection.manager:
                try:
                    if hasattr(connection.manager, 'test_connection'):
                        if not connection.manager.test_connection(connection.connection_id):
                            self.logger.warning(f"Connection {db_name} needs refresh")
                            # Attempt reconnection
                            try:
                                new_connection_id = connection.manager.connect_to_database(db_name)
                                connection.connection_id = new_connection_id
                                connection.status = 'CONNECTED'
                                connection.last_activity = datetime.now()
                                connection.error_message = None
                                self.logger.info(f"Refreshed connection to {db_name}")
                            except Exception as e:
                                self.logger.error(f"Failed to refresh connection to {db_name}: {e}")
                                connection.status = 'DISCONNECTED'
                                connection.error_message = str(e)
                        else:
                            connection.last_activity = datetime.now()
                            self.logger.debug(f"Connection to {db_name} is healthy")
                except Exception as e:
                    self.logger.error(f"Error testing connection to {db_name}: {e}")
                    connection.status = 'ERROR'
                    connection.error_message = str(e)
    
    def _scan_single_database(self, 
                            db_name: str,
                            table_list: List[str],
                            sample_size: int,
                            confidence_threshold: float) -> MultiDatabaseScanResult:
        """Scan a single database for PII (used in thread pool)"""
        start_time = time.time()
        
        try:
            connection = self.connections[db_name]
            if connection.status != 'CONNECTED':
                raise Exception(f"Database {db_name} not connected")
            
            # Import here to avoid circular imports
            from pii_detector import PIIDetector
            
            pii_detector = PIIDetector()
            total_pii_instances = 0
            tables_scanned = 0
            table_results = []
            
            for table_name in table_list:
                try:
                    # Parse schema and table
                    if '.' in table_name:
                        schema, table = table_name.split('.', 1)
                    else:
                        schema, table = 'dbo', table_name
                    
                    # Get sample data
                    sample_data = connection.manager.sample_table_data(
                        connection.connection_id, schema, table, sample_size
                    )
                    
                    if sample_data is not None and not sample_data.empty:
                        # Run PII detection
                        analyses = pii_detector.analyze_dataframe(sample_data, f"{db_name}.{table_name}")
                        
                        # Count PII instances
                        table_pii_count = sum(len(analysis.pii_matches) for analysis in analyses)
                        total_pii_instances += table_pii_count
                        
                        # Store table results
                        table_results.append({
                            'database': db_name,
                            'table': table_name,
                            'pii_instances': table_pii_count,
                            'columns_analyzed': len(analyses),
                            'analyses': analyses
                        })
                        
                        tables_scanned += 1
                        
                    else:
                        self.logger.warning(f"No data retrieved from {db_name}.{table_name}")
                        
                except Exception as table_error:
                    self.logger.error(f"Error scanning table {db_name}.{table_name}: {table_error}")
                    # Continue with other tables
                    continue
            
            duration = time.time() - start_time
            
            return MultiDatabaseScanResult(
                database_name=db_name,
                tables_scanned=tables_scanned,
                pii_instances_found=total_pii_instances,
                scan_duration=duration,
                status='COMPLETED' if tables_scanned > 0 else 'PARTIAL',
                table_results=table_results
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Database scan failed for {db_name}: {e}")
            
            return MultiDatabaseScanResult(
                database_name=db_name,
                tables_scanned=0,
                pii_instances_found=0,
                scan_duration=duration,
                status='FAILED',
                error_message=str(e)
            )
    
    def test_all_connections(self) -> Dict[str, bool]:
        """Test all database connections"""
        results = {}
        
        for db_name, connection in self.connections.items():
            if connection.status == 'CONNECTED':
                try:
                    is_alive = connection.manager.test_connection(connection.connection_id)
                    results[db_name] = is_alive
                    
                    if not is_alive:
                        connection.status = 'ERROR'
                        connection.error_message = "Connection test failed"
                        
                except Exception as e:
                    results[db_name] = False
                    connection.status = 'ERROR'
                    connection.error_message = str(e)
            else:
                results[db_name] = False
        
        return results
    
    def disconnect_all(self):
        """Disconnect from all databases"""
        for db_name, connection in self.connections.items():
            if connection.status == 'CONNECTED':
                try:
                    connection.manager.disconnect(connection.connection_id)
                    connection.status = 'DISCONNECTED'
                    self.logger.info(f"Disconnected from {db_name}")
                except Exception as e:
                    self.logger.error(f"Error disconnecting from {db_name}: {e}")
        
        self.connections.clear()
    
    def get_connection_summary(self) -> Dict[str, Any]:
        """Get summary of all database connections"""
        summary = {
            'total_connections': len(self.connections),
            'connected': 0,
            'disconnected': 0,
            'errors': 0,
            'databases': []
        }
        
        for db_name, connection in self.connections.items():
            if connection.status == 'CONNECTED':
                summary['connected'] += 1
            elif connection.status == 'DISCONNECTED':
                summary['disconnected'] += 1
            else:
                summary['errors'] += 1
            
            summary['databases'].append({
                'name': db_name,
                'status': connection.status,
                'last_activity': connection.last_activity,
                'error_message': connection.error_message
            })
        
        return summary
    
    def __del__(self):
        """Cleanup connections when manager is destroyed"""
        try:
            self.disconnect_all()
            self.executor.shutdown(wait=True)
        except:
            pass

# Global multi-database manager instance
multi_db_manager = MultiDatabaseManager()
