"""
PII Detection Report Generator
Generates comprehensive compliance and analysis reports
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import json
from config import PII_PATTERNS

class PIIReportGenerator:
    """Generates comprehensive PII detection reports"""
    
    def __init__(self):
        pass
    
    def generate_executive_summary(self, analysis_results: Dict) -> Dict:
        """Generate executive summary report"""
        summary = analysis_results['summary']
        analyses = analysis_results['analyses']
        
        # Risk assessment
        high_risk_columns = [a for a in analyses if a.risk_score >= 0.7]
        critical_pii_types = []
        
        for analysis in high_risk_columns:
            for match in analysis.pii_matches:
                pii_config = PII_PATTERNS.get(match.pattern_type, {})
                if pii_config.get('severity') == 'CRITICAL':
                    critical_pii_types.append(match.pattern_type)
        
        critical_pii_types = list(set(critical_pii_types))
        
        # Compliance exposure
        regulation_exposure = {'GDPR': 0, 'CCPA': 0, 'HIPAA': 0}
        
        for analysis in analyses:
            for match in analysis.pii_matches:
                pii_config = PII_PATTERNS.get(match.pattern_type, {})
                regulations = pii_config.get('regulations', [])
                for reg in regulations:
                    if reg in regulation_exposure:
                        regulation_exposure[reg] += 1
        
        return {
            'scan_date': analysis_results['scan_time'].isoformat(),
            'database_scope': analysis_results['tables_scanned'],
            'total_columns_analyzed': summary['total_columns_analyzed'],
            'high_risk_findings': len(high_risk_columns),
            'critical_pii_types': critical_pii_types,
            'regulation_exposure': regulation_exposure,
            'risk_level': self._calculate_overall_risk_level(analyses),
            'immediate_actions_required': len(high_risk_columns) > 0,
            'compliance_gaps': self._identify_compliance_gaps(analyses)
        }
    
    def generate_detailed_findings_report(self, analysis_results: Dict) -> List[Dict]:
        """Generate detailed findings report"""
        analyses = analysis_results['analyses']
        detailed_findings = []
        
        for analysis in analyses:
            if analysis.pii_matches:  # Only include columns with findings
                finding = {
                    'column_name': analysis.column_name,
                    'risk_score': analysis.risk_score,
                    'risk_level': self._get_risk_level(analysis.risk_score),
                    'data_type': analysis.data_type,
                    'total_rows': analysis.total_rows,
                    'non_null_rows': analysis.non_null_rows,
                    'unique_values': analysis.unique_values,
                    'pii_findings': []
                }
                
                for match in analysis.pii_matches:
                    pii_config = PII_PATTERNS.get(match.pattern_type, {})
                    pii_finding = {
                        'pii_type': match.pattern_type,
                        'description': pii_config.get('description', 'Unknown'),
                        'severity': pii_config.get('severity', 'LOW'),
                        'regulations': pii_config.get('regulations', []),
                        'confidence': match.confidence,
                        'sample_value_masked': self._mask_value(match.value, match.pattern_type),
                        'recommended_actions': self._get_recommended_actions(match.pattern_type, pii_config)
                    }
                    finding['pii_findings'].append(pii_finding)
                
                detailed_findings.append(finding)
        
        return detailed_findings
    
    def generate_compliance_report(self, analysis_results: Dict) -> Dict:
        """Generate compliance-focused report"""
        analyses = analysis_results['analyses']
        
        compliance_report = {
            'gdpr_compliance': self._analyze_gdpr_compliance(analyses),
            'ccpa_compliance': self._analyze_ccpa_compliance(analyses),
            'hipaa_compliance': self._analyze_hipaa_compliance(analyses),
            'recommendations': self._generate_compliance_recommendations(analyses)
        }
        
        return compliance_report
    
    def _analyze_gdpr_compliance(self, analyses: List) -> Dict:
        """Analyze GDPR compliance"""
        gdpr_findings = []
        special_categories = []
        
        for analysis in analyses:
            for match in analysis.pii_matches:
                pii_config = PII_PATTERNS.get(match.pattern_type, {})
                if 'GDPR' in pii_config.get('regulations', []):
                    gdpr_findings.append({
                        'column': analysis.column_name,
                        'type': match.pattern_type,
                        'severity': pii_config.get('severity', 'LOW')
                    })
                    
                    # Check for special categories
                    if match.pattern_type in [
                        'RACIAL_ETHNIC_ORIGIN', 'POLITICAL_OPINION', 'RELIGIOUS_BELIEF',
                        'TRADE_UNION', 'GENETIC_DATA', 'HEALTH_DATA', 'SEXUAL_ORIENTATION'
                    ]:
                        special_categories.append({
                            'column': analysis.column_name,
                            'type': match.pattern_type
                        })
        
        return {
            'total_findings': len(gdpr_findings),
            'special_categories_found': len(special_categories),
            'special_categories': special_categories,
            'risk_assessment': 'HIGH' if special_categories else 'MEDIUM' if gdpr_findings else 'LOW',
            'required_actions': [
                'Conduct Data Protection Impact Assessment (DPIA)' if special_categories else None,
                'Implement appropriate technical and organizational measures',
                'Ensure lawful basis for processing',
                'Update privacy policy and data processing agreements'
            ]
        }
    
    def _analyze_ccpa_compliance(self, analyses: List) -> Dict:
        """Analyze CCPA compliance"""
        ccpa_findings = []
        sensitive_categories = []
        
        for analysis in analyses:
            for match in analysis.pii_matches:
                pii_config = PII_PATTERNS.get(match.pattern_type, {})
                if 'CCPA' in pii_config.get('regulations', []):
                    ccpa_findings.append({
                        'column': analysis.column_name,
                        'type': match.pattern_type,
                        'severity': pii_config.get('severity', 'LOW')
                    })
                    
                    # Check for sensitive personal information
                    if match.pattern_type in [
                        'SSN', 'US_PASSPORT', 'DRIVERS_LICENSE', 'CREDIT_CARD',
                        'GEOLOCATION', 'RACIAL_ETHNIC_ORIGIN', 'RELIGIOUS_BELIEF',
                        'HEALTH_DATA', 'SEXUAL_ORIENTATION'
                    ]:
                        sensitive_categories.append({
                            'column': analysis.column_name,
                            'type': match.pattern_type
                        })
        
        return {
            'total_findings': len(ccpa_findings),
            'sensitive_categories_found': len(sensitive_categories),
            'sensitive_categories': sensitive_categories,
            'consumer_rights_impact': 'HIGH' if ccpa_findings else 'LOW',
            'required_actions': [
                'Implement consumer rights mechanisms (access, delete, opt-out)',
                'Update privacy policy with CCPA disclosures',
                'Implement data inventory and mapping',
                'Establish opt-out mechanisms for sensitive data' if sensitive_categories else None
            ]
        }
    
    def _analyze_hipaa_compliance(self, analyses: List) -> Dict:
        """Analyze HIPAA compliance"""
        phi_findings = []
        
        hipaa_identifiers = [
            'FULL_NAME', 'ADDRESS', 'DATE_OF_BIRTH', 'PHONE', 'FAX', 'EMAIL',
            'SSN', 'MEDICAL_RECORD_NUMBER', 'HEALTH_PLAN_NUMBER', 'ACCOUNT_NUMBER',
            'CERTIFICATE_LICENSE', 'VEHICLE_IDENTIFIER', 'DEVICE_IDENTIFIER',
            'URL', 'IP_ADDRESS', 'BIOMETRIC', 'HEALTH_DATA'
        ]
        
        for analysis in analyses:
            for match in analysis.pii_matches:
                if match.pattern_type in hipaa_identifiers:
                    phi_findings.append({
                        'column': analysis.column_name,
                        'phi_identifier': match.pattern_type,
                        'severity': PII_PATTERNS.get(match.pattern_type, {}).get('severity', 'LOW')
                    })
        
        return {
            'phi_identifiers_found': len(phi_findings),
            'phi_findings': phi_findings,
            'compliance_risk': 'HIGH' if phi_findings else 'LOW',
            'required_actions': [
                'Implement Business Associate Agreements (BAAs)',
                'Establish access controls and audit logs',
                'Implement encryption for PHI at rest and in transit',
                'Conduct risk assessments',
                'Implement minimum necessary access controls'
            ] if phi_findings else ['No HIPAA PHI detected - standard security measures recommended']
        }
    
    def _generate_compliance_recommendations(self, analyses: List) -> List[str]:
        """Generate overall compliance recommendations"""
        recommendations = []
        
        # Count high-risk findings
        high_risk_count = sum(1 for a in analyses if a.risk_score >= 0.7)
        critical_count = sum(
            1 for a in analyses 
            for m in a.pii_matches 
            if PII_PATTERNS.get(m.pattern_type, {}).get('severity') == 'CRITICAL'
        )
        
        if critical_count > 0:
            recommendations.extend([
                f"URGENT: {critical_count} critical PII findings require immediate attention",
                "Implement data encryption for all sensitive data at rest and in transit",
                "Establish strict access controls and monitoring"
            ])
        
        if high_risk_count > 0:
            recommendations.extend([
                f"Review and secure {high_risk_count} high-risk columns",
                "Implement data classification and handling procedures",
                "Conduct regular PII scanning and monitoring"
            ])
        
        recommendations.extend([
            "Establish comprehensive data governance framework",
            "Implement privacy by design principles",
            "Conduct regular compliance audits and assessments",
            "Provide privacy and security training to staff",
            "Maintain detailed data processing records"
        ])
        
        return recommendations
    
    def export_to_csv(self, findings: List[Dict], filename: str = None) -> str:
        """Export findings to CSV format"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pii_findings_{timestamp}.csv"
        
        # Flatten findings for CSV export
        flattened_findings = []
        
        for finding in findings:
            base_info = {
                'column_name': finding['column_name'],
                'risk_score': finding['risk_score'],
                'risk_level': finding['risk_level'],
                'data_type': finding['data_type'],
                'total_rows': finding['total_rows'],
                'non_null_rows': finding['non_null_rows'],
                'unique_values': finding['unique_values']
            }
            
            for pii_finding in finding['pii_findings']:
                row = base_info.copy()
                row.update({
                    'pii_type': pii_finding['pii_type'],
                    'description': pii_finding['description'],
                    'severity': pii_finding['severity'],
                    'regulations': ', '.join(pii_finding['regulations']),
                    'confidence': pii_finding['confidence'],
                    'recommended_actions': '; '.join(pii_finding['recommended_actions'])
                })
                flattened_findings.append(row)
        
        df = pd.DataFrame(flattened_findings)
        df.to_csv(filename, index=False)
        return filename
    
    def _mask_value(self, value: str, pii_type: str) -> str:
        """Mask PII value for reporting"""
        if len(value) <= 4:
            return "*" * len(value)
        return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level from score"""
        if risk_score >= 0.8:
            return 'CRITICAL'
        elif risk_score >= 0.6:
            return 'HIGH'
        elif risk_score >= 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_overall_risk_level(self, analyses: List) -> str:
        """Calculate overall risk level"""
        if not analyses:
            return 'LOW'
        
        max_risk = max(a.risk_score for a in analyses)
        return self._get_risk_level(max_risk)
    
    def _identify_compliance_gaps(self, analyses: List) -> List[str]:
        """Identify key compliance gaps"""
        gaps = []
        
        # Check for unprotected sensitive data
        high_risk_columns = [a for a in analyses if a.risk_score >= 0.7]
        if high_risk_columns:
            gaps.append("High-risk PII data lacks adequate protection")
        
        # Check for special categories
        special_categories = []
        for analysis in analyses:
            for match in analysis.pii_matches:
                if match.pattern_type in [
                    'RACIAL_ETHNIC_ORIGIN', 'HEALTH_DATA', 'GENETIC_DATA',
                    'SEXUAL_ORIENTATION', 'RELIGIOUS_BELIEF'
                ]:
                    special_categories.append(match.pattern_type)
        
        if special_categories:
            gaps.append("Special category data requires enhanced protection")
        
        return gaps
    
    def _get_recommended_actions(self, pii_type: str, pii_config: Dict) -> List[str]:
        """Get recommended actions for specific PII type"""
        severity = pii_config.get('severity', 'LOW')
        regulations = pii_config.get('regulations', [])
        
        actions = []
        
        if severity == 'CRITICAL':
            actions.extend([
                "Implement immediate access controls",
                "Encrypt data at rest and in transit",
                "Conduct security review"
            ])
        elif severity == 'HIGH':
            actions.extend([
                "Implement access logging",
                "Review data retention policies",
                "Consider data minimization"
            ])
        
        if 'GDPR' in regulations:
            actions.append("Ensure lawful basis for processing under GDPR")
        
        if 'HIPAA' in regulations:
            actions.append("Implement HIPAA safeguards and controls")
        
        if 'CCPA' in regulations:
            actions.append("Enable consumer rights under CCPA")
        
        return actions or ["Review data handling procedures"]
