"""
Utility functions for PII Detection prototype
"""

import re
import hashlib
import random
import string
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

def setup_logging(level: str = 'INFO') -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def mask_pii_value(value: str, pii_type: str) -> str:
    """Mask PII value for display purposes"""
    if not value:
        return value
    
    if pii_type == 'SSN':
        # Show only last 4 digits
        return f"XXX-XX-{value[-4:]}" if len(value) >= 4 else "XXX-XX-XXXX"
    
    elif pii_type == 'CREDIT_CARD':
        # Show only last 4 digits
        digits_only = re.sub(r'[^\d]', '', value)
        if len(digits_only) >= 4:
            return f"XXXX-XXXX-XXXX-{digits_only[-4:]}"
        return "XXXX-XXXX-XXXX-XXXX"
    
    elif pii_type == 'EMAIL':
        # Show first letter and domain
        if '@' in value:
            local, domain = value.split('@', 1)
            return f"{local[0]}***@{domain}" if local else f"***@{domain}"
        return "***@***.***"
    
    elif pii_type == 'PHONE':
        # Show only last 4 digits
        digits_only = re.sub(r'[^\d]', '', value)
        if len(digits_only) >= 4:
            return f"XXX-XXX-{digits_only[-4:]}"
        return "XXX-XXX-XXXX"
    
    elif pii_type in ['NAME', 'US_PASSPORT']:
        # Show first letter only
        return f"{value[0]}***" if value else "***"
    
    else:
        # Generic masking
        if len(value) <= 4:
            return "*" * len(value)
        return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"

def generate_synthetic_data(pii_type: str, count: int = 10) -> List[str]:
    """Generate synthetic data for testing purposes"""
    synthetic_data = []
    
    if pii_type == 'SSN':
        for _ in range(count):
            # Generate valid-looking SSN (not real)
            area = random.randint(100, 899)  # Avoid 000 and 900-999
            group = random.randint(10, 99)   # Avoid 00
            serial = random.randint(1000, 9999)  # Avoid 0000
            synthetic_data.append(f"{area:03d}-{group:02d}-{serial:04d}")
    
    elif pii_type == 'CREDIT_CARD':
        prefixes = ['4', '5', '3']  # Visa, MC, Amex
        for _ in range(count):
            prefix = random.choice(prefixes)
            if prefix == '4':  # Visa
                number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(15)])
            elif prefix == '5':  # MasterCard
                number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(15)])
            else:  # Amex
                number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(14)])
            
            # Format with dashes
            formatted = '-'.join([number[i:i+4] for i in range(0, len(number), 4)])
            synthetic_data.append(formatted)
    
    elif pii_type == 'EMAIL':
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'company.com', 'test.org']
        for _ in range(count):
            username = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
            domain = random.choice(domains)
            synthetic_data.append(f"{username}@{domain}")
    
    elif pii_type == 'PHONE':
        for _ in range(count):
            area_code = random.randint(200, 999)
            exchange = random.randint(200, 999)
            number = random.randint(1000, 9999)
            synthetic_data.append(f"({area_code}) {exchange}-{number}")
    
    return synthetic_data

def hash_pii_value(value: str, salt: str = "pii_detection_salt") -> str:
    """Create a hash of PII value for tracking purposes"""
    combined = f"{salt}{value}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]

def format_risk_score(score: float) -> Dict[str, Any]:
    """Format risk score with color and description"""
    if score >= 0.8:
        return {
            'score': score,
            'level': 'CRITICAL',
            'color': '#FF0000',
            'description': 'Immediate action required'
        }
    elif score >= 0.6:
        return {
            'score': score,
            'level': 'HIGH',
            'color': '#FF6600',
            'description': 'High risk - review recommended'
        }
    elif score >= 0.4:
        return {
            'score': score,
            'level': 'MEDIUM',
            'color': '#FFAA00',
            'description': 'Medium risk - monitor closely'
        }
    elif score >= 0.2:
        return {
            'score': score,
            'level': 'LOW',
            'color': '#FFDD00',
            'description': 'Low risk - periodic review'
        }
    else:
        return {
            'score': score,
            'level': 'MINIMAL',
            'color': '#00AA00',
            'description': 'Minimal risk detected'
        }

def export_results_to_csv(results: List[Dict], filename: str = None) -> str:
    """Export analysis results to CSV format"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pii_detection_results_{timestamp}.csv"
    
    # This would normally use pandas, but for prototype we'll return the filename
    return filename

def validate_connection_string(connection_string: str) -> bool:
    """Validate database connection string format"""
    required_parts = ['server', 'database']
    connection_lower = connection_string.lower()
    
    return all(part in connection_lower for part in required_parts)

def sanitize_table_name(table_name: str) -> str:
    """Sanitize table name for safe SQL usage"""
    # Remove any characters that aren't alphanumeric or underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '', table_name)
    
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = f"table_{sanitized}"
    
    return sanitized or "unknown_table"

def calculate_data_exposure_score(column_analyses: List[Any]) -> float:
    """Calculate overall data exposure score for a database/table"""
    if not column_analyses:
        return 0.0
    
    total_score = sum(analysis.risk_score for analysis in column_analyses)
    return min(total_score / len(column_analyses), 1.0)

def get_pii_severity_color(pii_type: str) -> str:
    """Get color code for PII type based on severity"""
    from config import PII_PATTERNS
    
    severity = PII_PATTERNS.get(pii_type, {}).get('severity', 'LOW')
    
    if severity == 'HIGH':
        return '#FF0000'  # Red
    elif severity == 'MEDIUM':
        return '#FF6600'  # Orange
    else:
        return '#FFAA00'  # Yellow

def create_anonymization_preview(original_value: str, pii_type: str) -> Dict[str, str]:
    """Create preview of how value would be anonymized"""
    return {
        'original': original_value,
        'masked': mask_pii_value(original_value, pii_type),
        'hashed': hash_pii_value(original_value),
        'type': pii_type
    }

def estimate_scan_time(num_tables: int, avg_rows_per_table: int) -> str:
    """Estimate scan time based on data volume"""
    total_rows = num_tables * avg_rows_per_table
    
    # Rough estimation: 1000 rows per second
    estimated_seconds = total_rows / 1000
    
    if estimated_seconds < 60:
        return f"{int(estimated_seconds)} seconds"
    elif estimated_seconds < 3600:
        minutes = int(estimated_seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        hours = int(estimated_seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''}"

def format_bytes(bytes_count: int) -> str:
    """Format bytes into human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"
