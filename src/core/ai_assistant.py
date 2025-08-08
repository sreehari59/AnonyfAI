"""
AI Assistant for PII Detection System
Integrates Claude API for intelligent table selection and PII analysis
"""

import anthropic
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from env_config import env_config

@dataclass
class TableRecommendation:
    table_name: str
    schema: str
    confidence_score: float
    reasoning: str
    estimated_pii_types: List[str]
    priority: str  # HIGH, MEDIUM, LOW

@dataclass
class PiiDecision:
    action: str  # MASK, LOG, ENCRYPT, IGNORE
    reasoning: str
    confidence: float
    encryption_key_hint: Optional[str] = None

class AIAssistant:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI Assistant with Claude API"""
        self.api_key = api_key or env_config.anthropic_api_key
        if not self.api_key or self.api_key == 'your_actual_claude_api_key_here':
            logging.warning("No Anthropic API key provided. AI features will be disabled.")
            self.client = None
        else:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                logging.error(f"Failed to initialize Anthropic client: {e}")
                self.client = None
        
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if AI assistant is available"""
        return self.client is not None
    
    def _estimate_token_count(self, text: str) -> int:
        """Estimate token count for text (rough approximation: ~4 chars per token)"""
        return len(text) // 4
    
    def _log_token_usage(self, prompt: str, batch_num: int, table_count: int):
        """Log token usage for debugging and optimization"""
        estimated_tokens = self._estimate_token_count(prompt)
        self.logger.info(f"Batch {batch_num}: {table_count} tables, ~{estimated_tokens} tokens ({estimated_tokens/1000:.1f}K)")
        
        if estimated_tokens > 180000:
            self.logger.warning(f"Batch {batch_num} approaching token limit: {estimated_tokens} tokens")
    
    def _optimize_batch_size(self, tables: List[Dict]) -> int:
        """Dynamically determine optimal batch size based on table complexity"""
        if not tables:
            return 50
        
        # Sample a few tables to estimate average size
        sample_size = min(5, len(tables))
        avg_table_size = 0
        
        for i in range(sample_size):
            table_json = json.dumps(tables[i], indent=1)
            avg_table_size += len(table_json)
        
        avg_table_size = avg_table_size // sample_size
        
        # Base prompt is ~1500 tokens, leave room for response (~2000 tokens)
        # Target ~180,000 tokens for safety (leaving 20k buffer from 200k limit)
        max_tables_tokens = 180000 - 3500  # 176,500 tokens for table data
        
        # Estimate tokens per table (rough: 4 chars per token)
        tokens_per_table = avg_table_size // 4
        
        if tokens_per_table > 0:
            optimal_batch_size = max(10, min(100, max_tables_tokens // tokens_per_table))
        else:
            optimal_batch_size = 50
        
        self.logger.info(f"Estimated {tokens_per_table} tokens per table, using batch size: {optimal_batch_size}")
        return optimal_batch_size
    
    async def analyze_tables_for_pii(self, tables: List[Dict[str, Any]]) -> List[TableRecommendation]:
        """
        Use AI to analyze table structures and recommend which ones likely contain PII
        Uses batch processing to handle large datasets within token limits
        
        Args:
            tables: List of table metadata (name, schema, columns, sample data)
        
        Returns:
            List of TableRecommendation objects ranked by PII likelihood
        """
        if not self.is_available():
            # Fallback to rule-based analysis
            return self._fallback_table_analysis(tables)
        
        try:
            # Filter out dbo schema tables first to reduce data size
            filtered_tables = [t for t in tables if t.get('schema', '').lower() != 'dbo']
            
            # Prepare table information for AI analysis with reduced data
            table_info = []
            for table in filtered_tables:
                # Limit column info to reduce token usage
                columns = table.get('columns', [])
                if len(columns) > 20:  # Limit columns per table
                    columns = columns[:20]
                
                table_summary = {
                    'name': table.get('table', 'Unknown'),
                    'schema': table.get('schema', 'Unknown'),
                    'columns': [col.get('column', 'Unknown') for col in columns if isinstance(col, dict)],
                    'row_count': table.get('row_count', 0)
                }
                table_info.append(table_summary)
            
            # Process tables in batches to avoid token limits
            batch_size = self._optimize_batch_size(table_info)
            all_recommendations = []
            
            for i in range(0, len(table_info), batch_size):
                batch = table_info[i:i + batch_size]
                batch_num = i//batch_size + 1
                total_batches = (len(table_info) + batch_size - 1)//batch_size
                
                self.logger.info(f"Processing batch {batch_num} of {total_batches} ({len(batch)} tables)")
                
                try:
                    # Create AI prompt for this batch
                    prompt = self._create_table_analysis_prompt(batch)
                    
                    # Log token usage for debugging
                    self._log_token_usage(prompt, batch_num, len(batch))
                    
                    # Double-check token count
                    estimated_tokens = self._estimate_token_count(prompt)
                    if estimated_tokens > 190000:  # Safety check
                        self.logger.warning(f"Batch {batch_num} estimated at {estimated_tokens} tokens, splitting further")
                        # Split this batch in half
                        mid = len(batch) // 2
                        smaller_batches = [batch[:mid], batch[mid:]] if mid > 0 else [batch]
                        
                        for sub_idx, sub_batch in enumerate(smaller_batches):
                            if sub_batch:  # Only process non-empty batches
                                sub_prompt = self._create_table_analysis_prompt(sub_batch)
                                self._log_token_usage(sub_prompt, f"{batch_num}.{sub_idx+1}", len(sub_batch))
                                
                                response = self.client.messages.create(
                                    model=env_config.ai_model_name,
                                    max_tokens=env_config.ai_max_tokens,
                                    temperature=env_config.ai_temperature,
                                    messages=[{"role": "user", "content": sub_prompt}]
                                )
                                batch_recommendations = self._parse_table_recommendations(response.content[0].text)
                                all_recommendations.extend(batch_recommendations)
                    else:
                        # Normal batch processing
                        response = self.client.messages.create(
                            model=env_config.ai_model_name,
                            max_tokens=env_config.ai_max_tokens,
                            temperature=env_config.ai_temperature,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        
                        # Parse AI response for this batch
                        batch_recommendations = self._parse_table_recommendations(response.content[0].text)
                        all_recommendations.extend(batch_recommendations)
                    
                except Exception as batch_error:
                    self.logger.warning(f"Batch {batch_num} failed: {str(batch_error)}, falling back to rule-based analysis")
                    # Fallback to rule-based for this batch
                    batch_tables = [filtered_tables[j] for j in range(i, min(i + batch_size, len(filtered_tables)))]
                    batch_fallback = self._fallback_table_analysis(batch_tables)
                    all_recommendations.extend(batch_fallback)
            
            # Sort all recommendations by confidence score
            all_recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            
            # Return top 30 recommendations
            return all_recommendations[:30]
            
        except Exception as e:
            self.logger.error(f"AI table analysis failed: {str(e)}")
            return self._fallback_table_analysis(tables)
    
    def _create_table_analysis_prompt(self, tables: List[Dict]) -> str:
        """Create prompt for AI table analysis"""
        tables_json = json.dumps(tables, indent=1)  # Compact JSON formatting
        
        return f"""
        As a data privacy expert, analyze these database tables and identify which ones are most likely to contain Personally Identifiable Information (PII).

        **CRITICAL REQUIREMENTS:**
        1. ⚠️ ALWAYS prioritize ANY table with name-related columns (firstname, lastname, fullname, name, personname, customer_name, employee_name, etc.)
        2. 🔴 ANY table with name columns MUST get HIGH priority with confidence 0.95+
        3. 🔍 Include tables like Person.Person, Employee tables, Customer tables, User tables
        4. 🚨 Name columns require 100% encryption priority
        5. ⚠️ Any table with sensitive data (e.g., health, financial) must be flagged for review.
        6. Please use the data to identify potential PII across all tables.
        7. Columns and data can be in any language.

        Tables to analyze:
        {tables_json}

        **COMPREHENSIVE NAME COLUMN DETECTION:**
        Look for these name patterns (case-insensitive):
        - firstname, first_name, fname, givenname, given_name
        - lastname, last_name, lname, surname, familyname, family_name
        - fullname, full_name, name, personname, person_name
        - customer_name, employee_name, user_name, display_name, legal_name
        - party_name, contact_name, business_name, company_name, trading_name
        - vendor_name, supplier_name, client_name, individual_name

        **ANALYSIS PRIORITY:**
        1. **NAME COLUMNS (CRITICAL)**: ANY table with name columns = AUTOMATIC HIGH priority (confidence 0.95+)
        2. **Other sensitive PII**: SSN, medical records, financial data = HIGH priority
        3. **Standard PII**: emails, addresses, phones = MEDIUM priority  
        4. **Minimal PII**: reference data = LOW priority

        **Expected Output Format:**
        [
          {{
            "table_name": "Person",
            "schema": "Person", 
            "confidence_score": 0.95,
            "reasoning": "🔴 CRITICAL: Contains FirstName, MiddleName, LastName columns requiring immediate encryption. Person table clearly contains personal identity data.",
            "estimated_pii_types": ["FULL_NAME", "FIRST_NAME", "LAST_NAME"],
            "priority": "HIGH"
          }},
          {{
            "table_name": "Employee",
            "schema": "HumanResources", 
            "confidence_score": 0.98,
            "reasoning": "🔴 CRITICAL: Employee table with name columns, birth dates, and contact information requiring encryption.",
            "estimated_pii_types": ["FULL_NAME", "DATE_OF_BIRTH", "NATIONAL_ID"],
            "priority": "HIGH"
          }}
        ]

        **IMPORTANT:** 
        - Return top {min(len(tables), 20)} tables ranked by PII likelihood
        - NEVER miss tables with name columns
        - Be aggressive in detecting name patterns
        - Any doubt about name columns = classify as HIGH priority
        """
    
    def _parse_table_recommendations(self, ai_response: str) -> List[TableRecommendation]:
        """Parse AI response into TableRecommendation objects"""
        try:
            # Extract JSON from AI response
            start_idx = ai_response.find('[')
            end_idx = ai_response.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON array found in AI response")
            
            json_str = ai_response[start_idx:end_idx]
            recommendations_data = json.loads(json_str)
            
            recommendations = []
            for item in recommendations_data:
                rec = TableRecommendation(
                    table_name=item.get('table_name', ''),
                    schema=item.get('schema', ''),
                    confidence_score=float(item.get('confidence_score', 0.0)),
                    reasoning=item.get('reasoning', ''),
                    estimated_pii_types=item.get('estimated_pii_types', []),
                    priority=item.get('priority', 'LOW')
                )
                recommendations.append(rec)
            
            # Sort by confidence score (highest first)
            recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI recommendations: {str(e)}")
            # Log the actual response for debugging
            self.logger.debug(f"AI response that failed to parse: {ai_response[:500]}...")
            return []
    
    def _fallback_table_analysis(self, tables: List[Dict[str, Any]]) -> List[TableRecommendation]:
        """Fallback rule-based table analysis when AI is not available"""
        recommendations = []
        
        # Common PII-indicating table name patterns
        high_priority_patterns = ['customer', 'user', 'person', 'employee', 'patient', 'member', 'contact', 'people']
        medium_priority_patterns = ['account', 'profile', 'record', 'data', 'info', 'detail', 'vendor', 'supplier']
        
        # ENHANCED: Much more comprehensive name-related patterns - these need 100% encryption
        critical_name_patterns = [
            # Direct name patterns
            'name', 'firstname', 'first_name', 'lastname', 'last_name', 'fullname', 'full_name',
            'personname', 'person_name', 'customer_name', 'employee_name', 'user_name', 'display_name',
            'givenname', 'given_name', 'surname', 'familyname', 'family_name', 'middlename', 'middle_name',
            'legal_name', 'party_name', 'contact_name', 'business_name', 'company_name', 'trading_name',
            'vendor_name', 'supplier_name', 'client_name', 'individual_name',
            # Common database naming variations
            'fname', 'lname', 'mname', 'displayname', 'contactname', 'personname', 'partyname',
            'namefirst', 'namelast', 'namemiddle', 'namefull', 'name_first', 'name_last', 'name_middle', 'name_full'
        ]
        
        # Other high-priority PII patterns  
        high_pii_patterns = ['email', 'phone', 'ssn', 'social', 'address', 'birth', 'dob']
        medium_pii_patterns = ['login', 'userid', 'account', 'number', 'id']
        
        for table in tables:
            table_name = table.get('table', '').lower()
            schema = table.get('schema', '')
            columns = table.get('columns', [])
            
            # ONLY skip dbo schema tables (not vendor tables in other schemas)
            if schema.lower() == 'dbo':
                continue
            
            # Analyze table name for PII likelihood
            priority = 'LOW'
            confidence = 0.1
            estimated_pii = []
            reasoning_parts = []
            
            # Check table name patterns
            for pattern in high_priority_patterns:
                if pattern in table_name:
                    priority = 'HIGH'
                    confidence += 0.4
                    reasoning_parts.append(f"Table name '{table_name}' suggests user/customer data")
                    break
            
            if priority != 'HIGH':
                for pattern in medium_priority_patterns:
                    if pattern in table_name:
                        priority = 'MEDIUM'
                        confidence += 0.2
                        reasoning_parts.append(f"Table name '{table_name}' may contain personal data")
                        break
            
            # CRITICAL: Check column names with AGGRESSIVE name detection
            column_names = [col.get('column', '').lower() for col in columns if isinstance(col, dict)]  # FIX: use 'column' not 'column_name'
            pii_columns_found = []
            name_columns_found = []
            
            # First pass: Look for ANY name patterns in column names
            for col_name in column_names:
                # CRITICAL: Check for name patterns first (highest priority)
                name_found = False
                for name_pattern in critical_name_patterns:
                    # More flexible matching - check if pattern is anywhere in column name
                    if name_pattern in col_name or col_name in name_pattern:
                        name_columns_found.append(col_name)
                        estimated_pii.append('FULL_NAME')  # Always classify name columns as FULL_NAME
                        confidence += 0.6  # HIGHER confidence boost for name columns
                        name_found = True
                        break
                
                if not name_found:
                    # Check other PII patterns
                    for pattern in high_pii_patterns:
                        if pattern in col_name:
                            pii_columns_found.append(col_name)
                            if 'email' in pattern:
                                estimated_pii.append('EMAIL')
                            elif 'phone' in pattern:
                                estimated_pii.append('PHONE')
                            elif 'ssn' in pattern or 'social' in pattern:
                                estimated_pii.append('SSN')
                            elif 'address' in pattern:
                                estimated_pii.append('ADDRESS')
                            elif 'birth' in pattern or 'dob' in pattern:
                                estimated_pii.append('DATE_OF_BIRTH')
                            confidence += 0.3
                            break
                    else:
                        # Check medium priority patterns
                        for pattern in medium_pii_patterns:
                            if pattern in col_name:
                                pii_columns_found.append(col_name)
                                estimated_pii.append('LOGIN_ID')
                                confidence += 0.15
                                break
            
            # ENHANCED: AUTOMATIC HIGH priority if ANY name columns found
            if name_columns_found:
                priority = 'HIGH'  # Any table with name columns gets HIGH priority
                confidence = max(confidence, 0.95)  # Ensure high confidence for name columns
                reasoning_parts.append(f"🔴 CRITICAL: Contains name columns requiring encryption: {', '.join(name_columns_found)}")
                reasoning_parts.append("Compliance: GDPR personal_data, HIPAA phi_identifier, CCPA personal_info")
            
            if pii_columns_found:
                reasoning_parts.append(f"Contains PII-indicating columns: {', '.join(pii_columns_found)}")
                # Add compliance risk based on PII types found
                if any('ssn' in col or 'social' in col for col in pii_columns_found):
                    reasoning_parts.append("Compliance: GDPR special_category, HIPAA phi_required, CCPA sensitive_personal_info")
                elif any('email' in col or 'phone' in col for col in pii_columns_found):
                    reasoning_parts.append("Compliance: GDPR personal_data, CCPA personal_info")
                
            # Adjust priority based on confidence
            if confidence > 0.8:
                priority = 'HIGH'
            elif confidence > 0.4:
                priority = 'MEDIUM'
            
            # Create recommendation for ALL tables with ANY PII potential (lowered threshold)
            if confidence > 0.05:  # Lower threshold to catch more tables
                reasoning = '. '.join(reasoning_parts) if reasoning_parts else "Standard table analysis"
                
                rec = TableRecommendation(
                    table_name=table.get('table', ''),
                    schema=schema,
                    confidence_score=min(confidence, 1.0),
                    reasoning=reasoning,
                    estimated_pii_types=list(set(estimated_pii)),
                    priority=priority
                )
                recommendations.append(rec)
        
        # Sort by confidence score (name tables will be highest)
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        return recommendations[:20]  # Return top 20 (increased from 15)
    
    async def suggest_pii_action(self, pii_type: str, value_sample: str, context: Dict[str, Any]) -> PiiDecision:
        """
        Use AI to suggest what action to take for detected PII
        
        Args:
            pii_type: Type of PII detected (e.g., 'EMAIL', 'SSN', 'PHONE')
            value_sample: Sample of the detected value (masked)
            context: Additional context (table name, column, regulation, etc.)
        
        Returns:
            PiiDecision with recommended action
        """
        if not self.is_available():
            return self._fallback_pii_decision(pii_type, context)
        
        try:
            prompt = self._create_pii_action_prompt(pii_type, value_sample, context)
            
            response = self.client.messages.create(
                model=env_config.ai_model_name,
                max_tokens=env_config.ai_max_tokens,
                temperature=env_config.ai_temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            decision = self._parse_pii_decision(response.content[0].text)
            return decision
            
        except Exception as e:
            self.logger.error(f"AI PII action suggestion failed: {str(e)}")
            return self._fallback_pii_decision(pii_type, context)
    
    def _create_pii_action_prompt(self, pii_type: str, value_sample: str, context: Dict[str, Any]) -> str:
        """Create prompt for PII action suggestion"""
        return f"""
        As a data privacy expert, recommend the appropriate action for this detected PII:

        PII Type: {pii_type}
        Sample Value: {value_sample}
        Context: {json.dumps(context, indent=2)}

        Consider:
        1. Sensitivity level of this PII type
        2. Regulatory requirements (GDPR, CCPA, HIPAA)
        3. Business context and data usage
        4. Security best practices

        Available actions:
        - MASK: Replace with asterisks or pseudonyms (for display/reporting)
        - LOG: Record the detection but don't modify data
        - ENCRYPT: Encrypt the data with a key (for storage)
        - IGNORE: No action needed (low risk)

        Return your recommendation as JSON:
        {{
            "action": "ENCRYPT",
            "reasoning": "Detailed explanation of why this action is recommended",
            "confidence": 0.85,
            "encryption_key_hint": "Optional hint for key derivation (if action is ENCRYPT)"
        }}
        """
    
    def _parse_pii_decision(self, ai_response: str) -> PiiDecision:
        """Parse AI response into PiiDecision object"""
        try:
            # Extract JSON from response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in AI response")
            
            json_str = ai_response[start_idx:end_idx]
            decision_data = json.loads(json_str)
            
            return PiiDecision(
                action=decision_data.get('action', 'LOG'),
                reasoning=decision_data.get('reasoning', ''),
                confidence=float(decision_data.get('confidence', 0.5)),
                encryption_key_hint=decision_data.get('encryption_key_hint')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI decision: {str(e)}")
            return PiiDecision(action='LOG', reasoning='AI parsing failed', confidence=0.3)
    
    def _fallback_pii_decision(self, pii_type: str, context: Dict[str, Any]) -> PiiDecision:
        """Fallback rule-based PII action decision"""
        # High-sensitivity PII types that should be encrypted
        high_sensitivity = ['SSN', 'CREDIT_CARD', 'MEDICAL_RECORD_NUMBER', 'HEALTH_DATA', 'BIOMETRIC']
        
        # Medium-sensitivity PII that should be masked
        medium_sensitivity = ['EMAIL', 'PHONE', 'FULL_NAME', 'ADDRESS', 'DATE_OF_BIRTH']
        
        if pii_type in high_sensitivity:
            return PiiDecision(
                action='ENCRYPT',
                reasoning=f'{pii_type} is high-sensitivity PII requiring encryption',
                confidence=0.8,
                encryption_key_hint=f'pii_{pii_type.lower()}_{datetime.now().strftime("%Y%m")}'
            )
        elif pii_type in medium_sensitivity:
            return PiiDecision(
                action='MASK',
                reasoning=f'{pii_type} should be masked for privacy protection',
                confidence=0.7
            )
        else:
            return PiiDecision(
                action='LOG',
                reasoning=f'{pii_type} is low-risk, logging detection is sufficient',
                confidence=0.6
            )
    
    async def analyze_column_values_for_compliance(self, table_name: str, column_name: str, 
                                                 column_values: List[str], suspected_pii_type: str) -> Dict[str, Any]:
        """
        Use AI to analyze actual column values for GDPR, CCPA, and HIPAA compliance requirements
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
            column_values: List of actual values from the column
            suspected_pii_type: Suspected PII type from discovery phase
        
        Returns:
            Dictionary with compliance analysis results
        """
        if not self.is_available():
            return self._fallback_compliance_analysis(column_values, suspected_pii_type)
        
        try:
            # Mask values for privacy while maintaining pattern recognition
            masked_values = []
            for value in column_values[:10]:  # Limit to first 10 values
                if value and len(str(value)) > 0:
                    value_str = str(value)
                    if len(value_str) > 6:
                        # Keep first 2 and last 2 characters, mask the middle
                        masked = value_str[:2] + '*' * (len(value_str) - 4) + value_str[-2:]
                    else:
                        # For short values, show pattern structure only
                        masked = ''.join(['A' if c.isalpha() else '9' if c.isdigit() else c for c in value_str])
                    masked_values.append(masked)
            
            # Create compliance analysis prompt
            prompt = self._create_compliance_analysis_prompt(
                table_name, column_name, masked_values, suspected_pii_type
            )
            
            # Call Claude API
            response = self.client.messages.create(
                model=env_config.ai_model_name,
                max_tokens=env_config.ai_max_tokens,
                temperature=env_config.ai_temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse AI response
            compliance_analysis = self._parse_compliance_analysis(response.content[0].text)
            return compliance_analysis
            
        except Exception as e:
            self.logger.error(f"AI compliance analysis failed: {str(e)}")
            return self._fallback_compliance_analysis(column_values, suspected_pii_type)
    
    def _create_compliance_analysis_prompt(self, table_name: str, column_name: str, 
                                         masked_values: List[str], suspected_pii_type: str) -> str:
        """Create prompt for AI compliance analysis"""
        values_sample = '\n'.join([f"  - {value}" for value in masked_values])
        
        return f"""
        As a data privacy and compliance expert specializing in GDPR, CCPA, and HIPAA regulations, 
        analyze the following database column values to determine encryption requirements.

        **Column Information:**
        - Table: {table_name}
        - Column: {column_name}
        - Suspected PII Type: {suspected_pii_type}
        - Sample Values (masked for privacy):
        {values_sample}

        **Analysis Requirements:**
        Please evaluate these values against major privacy regulations:

        1. **GDPR (General Data Protection Regulation)**:
           - Does this data qualify as "personal data" under GDPR Article 4?
           - Are these "special categories" of personal data (Article 9)?
           - Does this require explicit consent or legitimate interest?

        2. **CCPA (California Consumer Privacy Act)**:
           - Does this qualify as "personal information" under CCPA?
           - Are these "sensitive personal information" categories?
           - What consumer rights apply to this data?

        3. **HIPAA (Health Insurance Portability and Accountability Act)**:
           - Does this constitute Protected Health Information (PHI)?
           - Are these direct or indirect identifiers?
           - What safeguards are required?

        **Return your analysis as JSON:**
        {{
          "gdpr_classification": "personal_data|special_category|not_personal",
          "ccpa_classification": "personal_info|sensitive_personal_info|not_personal",
          "hipaa_classification": "phi|indirect_identifier|not_phi",
          "encryption_required": true/false,
          "encryption_urgency": "immediate|high|medium|low",
          "recommended_action": "encrypt|pseudonymize|mask|hash|log_only",
          "compliance_reasoning": "Detailed explanation based on regulatory requirements",
          "regulatory_citations": ["Specific regulation references"],
          "risk_level": "critical|high|medium|low",
          "data_subject_rights": ["right_to_erasure", "right_to_portability", "etc"],
          "retention_requirements": "Recommended data retention period",
          "confidence_score": 0.85
        }}

        Base your analysis on the actual data patterns you observe, not just the suspected PII type.
        """
    
    def _parse_compliance_analysis(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI compliance analysis response"""
        try:
            # Extract JSON from AI response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in compliance analysis response")
            
            json_str = ai_response[start_idx:end_idx]
            compliance_data = json.loads(json_str)
            
            # Ensure all required fields are present
            required_fields = [
                'gdpr_classification', 'ccpa_classification', 'hipaa_classification',
                'encryption_required', 'recommended_action', 'risk_level', 'confidence_score'
            ]
            
            for field in required_fields:
                if field not in compliance_data:
                    compliance_data[field] = 'unknown'
            
            return compliance_data
            
        except Exception as e:
            self.logger.error(f"Failed to parse compliance analysis: {str(e)}")
            return {
                'gdpr_classification': 'unknown',
                'ccpa_classification': 'unknown', 
                'hipaa_classification': 'unknown',
                'encryption_required': True,  # Default to safe side
                'recommended_action': 'encrypt',
                'risk_level': 'high',
                'confidence_score': 0.5,
                'compliance_reasoning': 'AI analysis failed, defaulting to high security',
                'parse_error': str(e)
            }
    
    def _fallback_compliance_analysis(self, column_values: List[str], suspected_pii_type: str) -> Dict[str, Any]:
        """Fallback compliance analysis when AI is not available"""
        # Rule-based compliance classification
        high_risk_types = ['EMAIL', 'SSN', 'PHONE', 'DATE_OF_BIRTH', 'NATIONAL_ID', 'MEDICAL_ID']
        medium_risk_types = ['FULL_NAME', 'FIRST_NAME', 'LAST_NAME', 'ADDRESS', 'LOGIN_ID']
        
        if suspected_pii_type in high_risk_types:
            return {
                'gdpr_classification': 'personal_data',
                'ccpa_classification': 'personal_info',
                'hipaa_classification': 'phi' if suspected_pii_type in ['SSN', 'MEDICAL_ID', 'DATE_OF_BIRTH'] else 'indirect_identifier',
                'encryption_required': True,
                'encryption_urgency': 'immediate',
                'recommended_action': 'encrypt',
                'risk_level': 'high',
                'confidence_score': 0.7,
                'compliance_reasoning': f'Rule-based analysis: {suspected_pii_type} is high-risk PII requiring encryption',
                'data_subject_rights': ['right_to_erasure', 'right_to_rectification', 'right_to_portability']
            }
        elif suspected_pii_type in medium_risk_types:
            return {
                'gdpr_classification': 'personal_data',
                'ccpa_classification': 'personal_info',
                'hipaa_classification': 'indirect_identifier',
                'encryption_required': True,
                'encryption_urgency': 'high',
                'recommended_action': 'pseudonymize',
                'risk_level': 'medium',
                'confidence_score': 0.6,
                'compliance_reasoning': f'Rule-based analysis: {suspected_pii_type} is medium-risk PII requiring protection',
                'data_subject_rights': ['right_to_erasure', 'right_to_rectification']
            }
        else:
            return {
                'gdpr_classification': 'not_personal',
                'ccpa_classification': 'not_personal',
                'hipaa_classification': 'not_phi',
                'encryption_required': False,
                'encryption_urgency': 'low',
                'recommended_action': 'log_only',
                'risk_level': 'low',
                'confidence_score': 0.4,
                'compliance_reasoning': f'Rule-based analysis: {suspected_pii_type} appears to be low-risk data',
                'data_subject_rights': []
            }

# Global AI assistant instance
try:
    ai_assistant = AIAssistant()
except Exception as e:
    logging.warning(f"Could not initialize global AI assistant: {e}")
    ai_assistant = None
