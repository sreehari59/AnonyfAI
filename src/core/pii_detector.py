"""
PII Detection Engine
Core logic for detecting personally identifiable information in data
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging
from dataclasses import dataclass
from config import PII_PATTERNS, PII_COLUMN_INDICATORS, SCAN_CONFIG

@dataclass
class PIIMatch:
    """Represents a PII match found in data"""
    pattern_type: str
    value: str
    confidence: float
    position: int
    column: str
    row_index: int

@dataclass
class ColumnAnalysis:
    """Analysis results for a column"""
    column_name: str
    data_type: str
    total_rows: int
    non_null_rows: int
    unique_values: int
    suspected_pii_types: List[str]
    pii_matches: List[PIIMatch]
    risk_score: float

class PIIDetector:
    """Main PII detection engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for PII detection"""
        compiled_patterns = {}
        for pii_type, config in PII_PATTERNS.items():
            try:
                compiled_patterns[pii_type] = re.compile(config['pattern'], re.IGNORECASE)
            except re.error as e:
                self.logger.error(f"Failed to compile pattern for {pii_type}: {e}")
        return compiled_patterns
    
    def analyze_column_name(self, column_name: str) -> List[str]:
        """Analyze column name for PII indicators"""
        suspected_types = []
        column_lower = column_name.lower()
        
        for indicator in PII_COLUMN_INDICATORS:
            if indicator in column_lower:
                # Map column indicators to PII types
                if any(x in indicator for x in ['ssn', 'social_security']):
                    suspected_types.append('SSN')
                elif any(x in indicator for x in ['email', 'e_mail']):
                    suspected_types.append('EMAIL')
                elif any(x in indicator for x in ['phone', 'telephone', 'mobile']):
                    suspected_types.append('PHONE')
                elif any(x in indicator for x in ['credit_card', 'creditcard', 'cc_number']):
                    suspected_types.append('CREDIT_CARD')
                elif any(x in indicator for x in ['name', 'first_name', 'last_name']):
                    suspected_types.append('NAME')
                elif any(x in indicator for x in ['birth', 'dob']):
                    suspected_types.append('DATE_OF_BIRTH')
                elif any(x in indicator for x in ['passport']):
                    suspected_types.append('US_PASSPORT')
        
        return list(set(suspected_types))
    
    def detect_pii_in_text(self, text: str, column_name: str = "", row_index: int = -1) -> List[PIIMatch]:
        """Detect PII patterns in a text string"""
        if not isinstance(text, str) or not text.strip():
            return []
        
        matches = []
        for pii_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                confidence = self._calculate_confidence(pii_type, match.group(), column_name)
                
                pii_match = PIIMatch(
                    pattern_type=pii_type,
                    value=match.group(),
                    confidence=confidence,
                    position=match.start(),
                    column=column_name,
                    row_index=row_index
                )
                matches.append(pii_match)
        
        return matches
    
    def _calculate_confidence(self, pii_type: str, value: str, column_name: str) -> float:
        """Calculate confidence score for a PII match"""
        base_confidence = 0.7
        
        # Boost confidence if column name suggests this PII type
        suspected_types = self.analyze_column_name(column_name)
        if pii_type in suspected_types:
            base_confidence += 0.2
        
        # Additional validation for specific types
        if pii_type == 'SSN':
            base_confidence = self._validate_ssn(value)
        elif pii_type == 'CREDIT_CARD':
            base_confidence = self._validate_credit_card(value)
        elif pii_type == 'EMAIL':
            base_confidence = self._validate_email(value)
        
        return min(base_confidence, 1.0)
    
    def _validate_ssn(self, ssn: str) -> float:
        """Validate SSN format and rules"""
        # Remove formatting
        digits_only = re.sub(r'[^\d]', '', ssn)
        
        if len(digits_only) != 9:
            return 0.3
        
        # Check for invalid SSN patterns
        if digits_only == '000000000' or digits_only[:3] == '000' or digits_only[3:5] == '00':
            return 0.2
        
        return 0.9
    
    def _validate_credit_card(self, cc: str) -> float:
        """Validate credit card using Luhn algorithm"""
        # Remove formatting
        digits_only = re.sub(r'[^\d]', '', cc)
        
        if len(digits_only) < 13 or len(digits_only) > 19:
            return 0.3
        
        # Luhn algorithm
        def luhn_check(card_num):
            def digits_of(number):
                return [int(d) for d in str(number)]
            
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            
            for digit in even_digits:
                checksum += sum(digits_of(digit * 2))
            
            return checksum % 10 == 0
        
        if luhn_check(digits_only):
            return 0.95
        else:
            return 0.4
    
    def _validate_email(self, email: str) -> float:
        """Enhanced email validation"""
        # Basic checks
        if '@' not in email or '.' not in email:
            return 0.3
        
        parts = email.split('@')
        if len(parts) != 2:
            return 0.3
        
        local, domain = parts
        if not local or not domain:
            return 0.4
        
        # Check for valid TLD
        if '.' not in domain:
            return 0.5
        
        return 0.8
    
    def analyze_dataframe(self, df: pd.DataFrame, table_name: str = "") -> List[ColumnAnalysis]:
        """Analyze a DataFrame for PII"""
        results = []
        
        for column in df.columns:
            analysis = self.analyze_column(df, column, table_name)
            results.append(analysis)
        
        return results
    
    def analyze_column(self, df: pd.DataFrame, column_name: str, table_name: str = "") -> ColumnAnalysis:
        """Analyze a specific column for PII"""
        column_data = df[column_name]
        
        # Basic column statistics
        total_rows = len(column_data)
        non_null_rows = column_data.notna().sum()
        unique_values = column_data.nunique()
        
        # Analyze column name for PII indicators
        suspected_types = self.analyze_column_name(column_name)
        
        # Analyze actual data
        all_matches = []
        sample_size = min(SCAN_CONFIG['sample_size'], non_null_rows)
        
        if sample_size > 0:
            # Sample data for analysis
            sample_data = column_data.dropna().sample(n=sample_size, random_state=42)
            
            for idx, value in sample_data.items():
                if pd.isna(value):
                    continue
                
                value_str = str(value)
                matches = self.detect_pii_in_text(value_str, column_name, idx)
                all_matches.extend(matches)
        
        # Calculate risk score
        risk_score = self._calculate_column_risk_score(
            suspected_types, all_matches, non_null_rows
        )
        
        return ColumnAnalysis(
            column_name=column_name,
            data_type=str(column_data.dtype),
            total_rows=total_rows,
            non_null_rows=non_null_rows,
            unique_values=unique_values,
            suspected_pii_types=suspected_types,
            pii_matches=all_matches,
            risk_score=risk_score
        )
    
    def _calculate_column_risk_score(self, suspected_types: List[str], matches: List[PIIMatch], total_rows: int) -> float:
        """Calculate risk score for a column"""
        if total_rows == 0:
            return 0.0
        
        # Base score from column name analysis
        base_score = len(suspected_types) * 0.2
        
        # Score from actual PII matches
        high_confidence_matches = [m for m in matches if m.confidence >= SCAN_CONFIG['confidence_threshold']]
        match_ratio = len(high_confidence_matches) / max(total_rows, 1)
        match_score = min(match_ratio * 2, 0.8)  # Cap at 0.8
        
        # Severity bonus
        severity_bonus = 0
        for match in high_confidence_matches:
            severity = PII_PATTERNS.get(match.pattern_type, {}).get('severity', 'LOW')
            if severity == 'HIGH':
                severity_bonus += 0.1
            elif severity == 'MEDIUM':
                severity_bonus += 0.05
        
        total_score = base_score + match_score + min(severity_bonus, 0.3)
        return min(total_score, 1.0)
    
    def generate_summary_report(self, analyses: List[ColumnAnalysis]) -> Dict[str, Any]:
        """Generate summary report from column analyses"""
        total_columns = len(analyses)
        high_risk_columns = [a for a in analyses if a.risk_score >= 0.7]
        medium_risk_columns = [a for a in analyses if 0.4 <= a.risk_score < 0.7]
        
        pii_types_found = set()
        total_pii_instances = 0
        
        for analysis in analyses:
            for match in analysis.pii_matches:
                pii_types_found.add(match.pattern_type)
                total_pii_instances += 1
        
        return {
            'total_columns_analyzed': total_columns,
            'high_risk_columns': len(high_risk_columns),
            'medium_risk_columns': len(medium_risk_columns),
            'low_risk_columns': total_columns - len(high_risk_columns) - len(medium_risk_columns),
            'pii_types_detected': list(pii_types_found),
            'total_pii_instances': total_pii_instances,
            'high_risk_column_names': [a.column_name for a in high_risk_columns],
            'recommendations': self._generate_recommendations(analyses)
        }
    
    def _generate_recommendations(self, analyses: List[ColumnAnalysis]) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        high_risk_columns = [a for a in analyses if a.risk_score >= 0.7]
        
        if high_risk_columns:
            recommendations.append(
                f"Immediate attention required: {len(high_risk_columns)} columns contain high-risk PII data"
            )
            
            for col in high_risk_columns:
                pii_types = set(m.pattern_type for m in col.pii_matches)
                recommendations.append(
                    f"Column '{col.column_name}' contains {', '.join(pii_types)} - consider encryption or tokenization"
                )
        
        # Check for columns with PII-like names but no data matches
        name_only_suspects = [
            a for a in analyses 
            if a.suspected_pii_types and not a.pii_matches and a.risk_score < 0.3
        ]
        
        if name_only_suspects:
            recommendations.append(
                f"Review column names: {len(name_only_suspects)} columns have PII-suggestive names but no detected content"
            )
        
        return recommendations
