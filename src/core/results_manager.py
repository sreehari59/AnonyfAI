"""
Results Database Manager
Handles insertion of PII detection results into a dedicated results table
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import uuid
import os
from env_config import env_config

@dataclass
class PiiDetectionResult:
    """Represents a single PII detection result"""
    scan_id: str
    database_name: str
    schema_name: str
    table_name: str
    column_name: str
    pii_type: str
    confidence_score: float
    sample_value_masked: str
    action_taken: str  # MASK, LOG, ENCRYPT, IGNORE
    encryption_key_hint: Optional[str]
    detected_at: datetime
    ai_reasoning: Optional[str] = None
    regulatory_flags: Optional[str] = None  # JSON string of applicable regulations

@dataclass
class ScanSession:
    """Represents a complete PII detection scan session"""
    scan_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    databases_scanned: List[str]
    tables_scanned: int
    pii_instances_found: int
    ai_recommendations_used: bool
    status: str  # RUNNING, COMPLETED, FAILED

class ResultsManager:
    def __init__(self, results_db_path: Optional[str] = None):
        """Initialize the results database manager"""
        self.db_path = results_db_path or env_config.results_db_path
        self.logger = logging.getLogger(__name__)
        self._initialize_database()
    
    def _initialize_database(self):
        """Create the results database and tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create scan sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scan_sessions (
                        scan_id TEXT PRIMARY KEY,
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP,
                        databases_scanned TEXT,  -- JSON array
                        tables_scanned INTEGER,
                        pii_instances_found INTEGER,
                        ai_recommendations_used BOOLEAN,
                        status TEXT
                    )
                """)
                
                # Check if identified_names_team_epsilon table exists, if not create it
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS identified_names_team_epsilon (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,  -- encrypted value that is sensitive
                        source TEXT,  -- dbname.tablename format
                        probability REAL,  -- probability that it is sensitive
                        key TEXT,  -- primary key reference
                        encrypt_key TEXT  -- encryption key used
                    )
                """)
                
                # Create scan sessions table (for tracking and metadata)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scan_sessions (
                        scan_id TEXT PRIMARY KEY,
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP,
                        databases_scanned TEXT,  -- JSON array
                        tables_scanned INTEGER,
                        pii_instances_found INTEGER,
                        ai_recommendations_used BOOLEAN,
                        status TEXT
                    )
                """)
                
                # Create detailed results table (for backward compatibility and detailed analysis)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pii_detection_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scan_id TEXT,
                        database_name TEXT,
                        schema_name TEXT,
                        table_name TEXT,
                        column_name TEXT,
                        pii_type TEXT,
                        confidence_score REAL,
                        sample_value_masked TEXT,
                        action_taken TEXT,
                        encryption_key_hint TEXT,
                        detected_at TIMESTAMP,
                        ai_reasoning TEXT,
                        regulatory_flags TEXT,
                        FOREIGN KEY (scan_id) REFERENCES scan_sessions (scan_id)
                    )
                """)
                
                # Create indexes for better performance (only if they don't exist)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON identified_names_team_epsilon(source)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_probability ON identified_names_team_epsilon(probability)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_id ON pii_detection_results(scan_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_pii_type ON pii_detection_results(pii_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_table ON pii_detection_results(database_name, table_name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_detected_at ON pii_detection_results(detected_at)")
                
                # Create summary view for reporting
                cursor.execute("""
                    CREATE VIEW IF NOT EXISTS pii_summary AS
                    SELECT 
                        database_name,
                        table_name,
                        pii_type,
                        COUNT(*) as instance_count,
                        AVG(confidence_score) as avg_confidence,
                        MAX(detected_at) as last_detected,
                        GROUP_CONCAT(DISTINCT action_taken) as actions_taken
                    FROM pii_detection_results
                    GROUP BY database_name, table_name, pii_type
                """)
                
                conn.commit()
                self.logger.info(f"Results database initialized at {self.db_path}")
                
                # Check if existing identified_names_team_epsilon table has expected columns
                self._verify_existing_table_structure()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize results database: {str(e)}")
            raise
    
    def _verify_existing_table_structure(self):
        """Verify that the existing identified_names_team_epsilon table has the expected columns"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get table info
                cursor.execute("PRAGMA table_info(identified_names_team_epsilon)")
                columns = cursor.fetchall()
                
                if columns:
                    column_names = [col[1] for col in columns]
                    expected_columns = ['id', 'name', 'source', 'probability', 'key', 'encrypt_key']
                    
                    self.logger.info(f"Found existing table with columns: {column_names}")
                    
                    # Check if all expected columns exist
                    missing_columns = [col for col in expected_columns if col not in column_names]
                    
                    if missing_columns:
                        self.logger.warning(f"Missing columns in existing table: {missing_columns}")
                        # Could add ALTER TABLE statements here if needed
                    else:
                        self.logger.info("Existing table structure matches expected format")
                else:
                    self.logger.info("Table identified_names_team_epsilon doesn't exist yet, will be created on first use")
                    
        except Exception as e:
            self.logger.warning(f"Could not verify table structure: {e}")
            # Continue anyway as the CREATE TABLE IF NOT EXISTS will handle missing table
    
    def start_scan_session(self, databases: List[str], ai_enabled: bool = True) -> str:
        """Start a new scan session and return the scan ID"""
        scan_id = str(uuid.uuid4())
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO scan_sessions 
                    (scan_id, started_at, databases_scanned, tables_scanned, 
                     pii_instances_found, ai_recommendations_used, status)
                    VALUES (?, ?, ?, 0, 0, ?, 'RUNNING')
                """, (scan_id, datetime.now(), json.dumps(databases), ai_enabled))
                conn.commit()
                
            self.logger.info(f"Started scan session {scan_id} for databases: {databases}")
            return scan_id
            
        except Exception as e:
            self.logger.error(f"Failed to start scan session: {str(e)}")
            raise
    
    def insert_pii_result(self, result: PiiDetectionResult):
        """Insert a single PII detection result"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO pii_detection_results 
                    (scan_id, database_name, schema_name, table_name, column_name,
                     pii_type, confidence_score, sample_value_masked, action_taken,
                     encryption_key_hint, detected_at, ai_reasoning, regulatory_flags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.scan_id, result.database_name, result.schema_name,
                    result.table_name, result.column_name, result.pii_type,
                    result.confidence_score, result.sample_value_masked,
                    result.action_taken, result.encryption_key_hint,
                    result.detected_at, result.ai_reasoning, result.regulatory_flags
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to insert PII result: {str(e)}")
            raise
    
    def bulk_insert_pii_results(self, results: List[PiiDetectionResult]):
        """Insert multiple PII detection results in a batch"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                data = []
                for result in results:
                    data.append((
                        result.scan_id, result.database_name, result.schema_name,
                        result.table_name, result.column_name, result.pii_type,
                        result.confidence_score, result.sample_value_masked,
                        result.action_taken, result.encryption_key_hint,
                        result.detected_at, result.ai_reasoning, result.regulatory_flags
                    ))
                
                cursor.executemany("""
                    INSERT INTO pii_detection_results 
                    (scan_id, database_name, schema_name, table_name, column_name,
                     pii_type, confidence_score, sample_value_masked, action_taken,
                     encryption_key_hint, detected_at, ai_reasoning, regulatory_flags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, data)
                
                conn.commit()
                self.logger.info(f"Bulk inserted {len(results)} PII detection results")
                
        except Exception as e:
            self.logger.error(f"Failed to bulk insert PII results: {str(e)}")
            raise
    
    def insert_identified_pii_result(self, name: str, source: str, probability: float, 
                                   key: str, encrypt_key: str):
        """Insert a single result into the identified_names_team_epsilon table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO identified_names_team_epsilon 
                    (name, source, probability, key, encrypt_key)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, source, probability, key, encrypt_key))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to insert identified PII result: {str(e)}")
            raise
    
    def bulk_insert_identified_pii_results(self, results: List[Dict[str, Any]]):
        """Insert multiple results into the identified_names_team_epsilon table
        
        Args:
            results: List of dictionaries with keys: name, source, probability, key, encrypt_key
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                data = []
                for result in results:
                    data.append((
                        result['name'],
                        result['source'], 
                        result['probability'],
                        result['key'],
                        result['encrypt_key']
                    ))
                
                cursor.executemany("""
                    INSERT INTO identified_names_team_epsilon 
                    (name, source, probability, key, encrypt_key)
                    VALUES (?, ?, ?, ?, ?)
                """, data)
                
                conn.commit()
                self.logger.info(f"Bulk inserted {len(results)} identified PII results")
                
        except Exception as e:
            self.logger.error(f"Failed to bulk insert identified PII results: {str(e)}")
            raise
    
    def get_identified_pii_results(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get results from the identified_names_team_epsilon table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, name, source, probability, key, encrypt_key 
                    FROM identified_names_team_epsilon 
                    ORDER BY id DESC
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    results.append({
                        'id': row[0],
                        'name': row[1],
                        'source': row[2], 
                        'probability': row[3],
                        'key': row[4],
                        'encrypt_key': row[5]
                    })
                
                return results
                
        except Exception as e:
            self.logger.error(f"Failed to get identified PII results: {str(e)}")
            raise
    
    def complete_scan_session(self, scan_id: str, tables_scanned: int, pii_instances: int):
        """Mark a scan session as completed and update statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE scan_sessions 
                    SET completed_at = ?, tables_scanned = ?, 
                        pii_instances_found = ?, status = 'COMPLETED'
                    WHERE scan_id = ?
                """, (datetime.now(), tables_scanned, pii_instances, scan_id))
                conn.commit()
                
            self.logger.info(f"Completed scan session {scan_id}: {tables_scanned} tables, {pii_instances} PII instances")
            
        except Exception as e:
            self.logger.error(f"Failed to complete scan session: {str(e)}")
            raise
    
    def fail_scan_session(self, scan_id: str, error_message: str):
        """Mark a scan session as failed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE scan_sessions 
                    SET completed_at = ?, status = 'FAILED'
                    WHERE scan_id = ?
                """, (datetime.now(), scan_id))
                conn.commit()
                
            self.logger.error(f"Scan session {scan_id} failed: {error_message}")
            
        except Exception as e:
            self.logger.error(f"Failed to mark scan session as failed: {str(e)}")
            raise
    
    def get_scan_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent scan session history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT scan_id, started_at, completed_at, databases_scanned,
                           tables_scanned, pii_instances_found, ai_recommendations_used, status
                    FROM scan_sessions 
                    ORDER BY started_at DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                history = []
                for row in rows:
                    record = dict(zip(columns, row))
                    # Parse JSON databases list
                    if record['databases_scanned']:
                        record['databases_scanned'] = json.loads(record['databases_scanned'])
                    history.append(record)
                
                return history
                
        except Exception as e:
            self.logger.error(f"Failed to get scan history: {str(e)}")
            return []
    
    def get_pii_summary_by_database(self, database_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get PII summary statistics grouped by database/table/type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if database_name:
                    cursor.execute("""
                        SELECT * FROM pii_summary 
                        WHERE database_name = ?
                        ORDER BY instance_count DESC
                    """, (database_name,))
                else:
                    cursor.execute("""
                        SELECT * FROM pii_summary 
                        ORDER BY database_name, instance_count DESC
                    """)
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get PII summary: {str(e)}")
            return []
    
    def get_results_for_scan(self, scan_id: str) -> List[Dict[str, Any]]:
        """Get all PII detection results for a specific scan"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM pii_detection_results 
                    WHERE scan_id = ?
                    ORDER BY detected_at DESC
                """, (scan_id,))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get results for scan {scan_id}: {str(e)}")
            return []
    
    def search_pii_results(self, 
                          database_name: Optional[str] = None,
                          table_name: Optional[str] = None,
                          pii_type: Optional[str] = None,
                          action_taken: Optional[str] = None,
                          min_confidence: Optional[float] = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Search PII results with various filters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM pii_detection_results WHERE 1=1"
                params = []
                
                if database_name:
                    query += " AND database_name = ?"
                    params.append(database_name)
                
                if table_name:
                    query += " AND table_name LIKE ?"
                    params.append(f"%{table_name}%")
                
                if pii_type:
                    query += " AND pii_type = ?"
                    params.append(pii_type)
                
                if action_taken:
                    query += " AND action_taken = ?"
                    params.append(action_taken)
                
                if min_confidence is not None:
                    query += " AND confidence_score >= ?"
                    params.append(min_confidence)
                
                query += " ORDER BY detected_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to search PII results: {str(e)}")
            return []
    
    def export_results_to_csv(self, scan_id: str, output_file: str):
        """Export scan results to CSV file"""
        try:
            import pandas as pd
            
            results = self.get_results_for_scan(scan_id)
            if results:
                df = pd.DataFrame(results)
                df.to_csv(output_file, index=False)
                self.logger.info(f"Exported {len(results)} results to {output_file}")
            else:
                self.logger.warning(f"No results found for scan {scan_id}")
                
        except ImportError:
            self.logger.error("pandas not available for CSV export")
        except Exception as e:
            self.logger.error(f"Failed to export results to CSV: {str(e)}")

# Global results manager instance
results_manager = ResultsManager()
