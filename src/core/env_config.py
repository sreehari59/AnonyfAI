"""
Environment Configuration Loader for PII Detection System
Loads environment variables from .env file and provides configuration access
"""

import os
from pathlib import Path
from typing import Optional, Union
import logging

# Try to load python-dotenv if available, otherwise use os.environ
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, use os.environ directly
    pass

class EnvironmentConfig:
    """Environment configuration manager for PII detection system"""
    
    def __init__(self):
        """Initialize environment configuration"""
        self._load_env_file()
    
    def _load_env_file(self):
        """Load .env file if it exists"""
        env_path = Path('.env')
        if env_path.exists():
            try:
                # Manual .env loading if python-dotenv is not available
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            if key not in os.environ:
                                os.environ[key] = value
            except Exception as e:
                logging.warning(f"Could not load .env file: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get environment variable value"""
        return os.environ.get(key, default)
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = self.get(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on', 'enabled')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer environment variable"""
        try:
            return int(self.get(key, str(default)))
        except ValueError:
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float environment variable"""
        try:
            return float(self.get(key, str(default)))
        except ValueError:
            return default
    
    # AI Configuration
    @property
    def anthropic_api_key(self) -> Optional[str]:
        """Get Anthropic API key"""
        return self.get('ANTHROPIC_API_KEY')
    
    @property
    def ai_model_name(self) -> str:
        """Get AI model name"""
        return self.get('AI_MODEL_NAME', 'claude-3-sonnet-20240229')
    
    @property
    def ai_max_tokens(self) -> int:
        """Get AI max tokens"""
        return self.get_int('AI_MAX_TOKENS', 4000)
    
    @property
    def ai_temperature(self) -> float:
        """Get AI temperature"""
        return self.get_float('AI_TEMPERATURE', 0.1)
    
    # Database Configuration
    @property
    def connection_mode(self) -> str:
        """Get connection mode"""
        return self.get('CONNECTION_MODE', 'demo')
    
    @property
    def db_server(self) -> str:
        """Get database server"""
        return self.get('DB_SERVER', 'localhost')
    
    @property
    def db_username(self) -> str:
        """Get database username"""
        return self.get('DB_USERNAME', '')
    
    @property
    def db_password(self) -> str:
        """Get database password"""
        return self.get('DB_PASSWORD', '')
    
    @property
    def db_port(self) -> int:
        """Get database port"""
        return self.get_int('DB_PORT', 1433)
    
    @property
    def default_database(self) -> str:
        """Get default database"""
        return self.get('DEFAULT_DATABASE', 'master')
    
    # Encryption Configuration
    @property
    def master_key_file(self) -> str:
        """Get master key file path"""
        return self.get('MASTER_KEY_FILE', 'master.key')
    
    @property
    def key_derivation_iterations(self) -> int:
        """Get key derivation iterations"""
        return self.get_int('KEY_DERIVATION_ITERATIONS', 100000)
    
    # Scanning Configuration
    @property
    def default_sample_size(self) -> int:
        """Get default sample size"""
        return self.get_int('DEFAULT_SAMPLE_SIZE', 100)
    
    @property
    def max_rows_to_scan(self) -> int:
        """Get max rows to scan"""
        return self.get_int('MAX_ROWS_TO_SCAN', 10000)
    
    @property
    def confidence_threshold(self) -> float:
        """Get confidence threshold"""
        return self.get_float('CONFIDENCE_THRESHOLD', 0.7)
    
    @property
    def max_concurrent_scans(self) -> int:
        """Get max concurrent scans"""
        return self.get_int('MAX_CONCURRENT_SCANS', 5)
    
    # Results Database Configuration
    @property
    def results_db_path(self) -> str:
        """Get results database path"""
        return self.get('RESULTS_DB_PATH', 'pii_results.db')
    
    @property
    def auto_backup(self) -> bool:
        """Get auto backup setting"""
        return self.get_bool('AUTO_BACKUP', True)
    
    @property
    def backup_retention_days(self) -> int:
        """Get backup retention days"""
        return self.get_int('BACKUP_RETENTION_DAYS', 30)
    
    # Logging Configuration
    @property
    def log_level(self) -> str:
        """Get log level"""
        return self.get('LOG_LEVEL', 'INFO')
    
    @property
    def log_file(self) -> str:
        """Get log file path"""
        return self.get('LOG_FILE', 'logs/pii_detection.log')
    
    # Streamlit Configuration
    @property
    def streamlit_host(self) -> str:
        """Get Streamlit host"""
        return self.get('STREAMLIT_HOST', 'localhost')
    
    @property
    def streamlit_port(self) -> int:
        """Get Streamlit port"""
        return self.get_int('STREAMLIT_PORT', 8501)
    
    @property
    def page_title(self) -> str:
        """Get page title"""
        return self.get('PAGE_TITLE', 'PII Detection System')
    
    @property
    def page_icon(self) -> str:
        """Get page icon"""
        return self.get('PAGE_ICON', '🔍')
    
    @property
    def layout(self) -> str:
        """Get layout"""
        return self.get('LAYOUT', 'wide')
    
    # Compliance Configuration
    @property
    def enable_gdpr_compliance(self) -> bool:
        """Get GDPR compliance setting"""
        return self.get_bool('ENABLE_GDPR_COMPLIANCE', True)
    
    @property
    def enable_ccpa_compliance(self) -> bool:
        """Get CCPA compliance setting"""
        return self.get_bool('ENABLE_CCPA_COMPLIANCE', True)
    
    @property
    def enable_hipaa_compliance(self) -> bool:
        """Get HIPAA compliance setting"""
        return self.get_bool('ENABLE_HIPAA_COMPLIANCE', True)
    
    @property
    def data_retention_period(self) -> int:
        """Get data retention period in days"""
        return self.get_int('DATA_RETENTION_PERIOD', 90)
    
    # Security Configuration
    @property
    def enable_data_masking(self) -> bool:
        """Get data masking setting"""
        return self.get_bool('ENABLE_DATA_MASKING', True)
    
    @property
    def enable_encryption(self) -> bool:
        """Get encryption setting"""
        return self.get_bool('ENABLE_ENCRYPTION', True)
    
    @property
    def session_timeout(self) -> int:
        """Get session timeout in seconds"""
        return self.get_int('SESSION_TIMEOUT', 3600)
    
    # Development Configuration
    @property
    def debug_mode(self) -> bool:
        """Get debug mode setting"""
        return self.get_bool('DEBUG_MODE', False)
    
    @property
    def cache_results(self) -> bool:
        """Get cache results setting"""
        return self.get_bool('CACHE_RESULTS', True)
    
    @property
    def mock_ai_responses(self) -> bool:
        """Get mock AI responses setting"""
        return self.get_bool('MOCK_AI_RESPONSES', False)
    
    def __repr__(self) -> str:
        """String representation of configuration"""
        return f"EnvironmentConfig(mode={self.connection_mode}, ai_enabled={bool(self.anthropic_api_key)})"

# Global configuration instance
env_config = EnvironmentConfig()

# Convenience functions
def get_env_config() -> EnvironmentConfig:
    """Get the global environment configuration instance"""
    return env_config

def is_ai_enabled() -> bool:
    """Check if AI features are enabled"""
    return bool(env_config.anthropic_api_key)

def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    return env_config.debug_mode

def get_db_config() -> dict:
    """Get database configuration as dictionary"""
    return {
        'server': env_config.db_server,
        'username': env_config.db_username,
        'password': env_config.db_password,
        'port': env_config.db_port,
        'database': env_config.default_database
    }

def get_scan_config() -> dict:
    """Get scanning configuration as dictionary"""
    return {
        'sample_size': env_config.default_sample_size,
        'max_rows': env_config.max_rows_to_scan,
        'confidence_threshold': env_config.confidence_threshold,
        'max_concurrent': env_config.max_concurrent_scans
    }
