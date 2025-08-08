"""
Configuration settings for PII Detection prototype
"""

# Database connection profiles
DATABASE_PROFILES = {
    'AdventureWorks2019': {
        'profile_id': '02767ADC-CD87-45CC-A7AB-3732D10EA6FE',
        'server': 'sql-lakeside-server.database.windows.net',
        'database': 'AdventureWorks2019',
        'username': 'hackathon_epsilon',
        'password': 'Qm7!dG3&yB5p',
        'port': 1433
    },
    'ECC60jkl_HACK': {
        'profile_id': '453BB2B9-4C5E-45F7-A811-7E386BC05DC2',
        'server': 'sql-lakeside-server.database.windows.net',
        'database': 'ECC60jkl_HACK',
        'username': 'hackathon_epsilon',
        'password': 'Qm7!dG3&yB5p',
        'port': 1433
    },
    'Jde920_demo': {
        'profile_id': 'DDBC1D0A-84C8-4AF2-B187-57FF4FBF97AF',
        'server': 'sql-lakeside-server.database.windows.net',
        'database': 'Jde920_demo',
        'username': 'hackathon_epsilon',
        'password': 'Qm7!dG3&yB5p',
        'port': 1433
    },
    'ORACLE_EBS_HACK': {
        'profile_id': '7F0F2390-E4F5-44F4-AD26-3CA05057E2E7',
        'server': 'sql-lakeside-server.database.windows.net',
        'database': 'ORACLE_EBS_HACK',
        'username': 'hackathon_epsilon',
        'password': 'Qm7!dG3&yB5p',
        'port': 1433
    },
    'Results': {
        'profile_id': 'AE52FB3C-DEEC-4047-B1AC-6F07E8CD2577',
        'server': 'sql-lakeside-server.database.windows.net',
        'database': 'Results',
        'username': 'hackathon_epsilon',
        'password': 'Qm7!dG3&yB5p',
        'port': 1433
    }
}

# PII Detection Patterns - Enhanced with GDPR, CCPA, and HIPAA compliance
PII_PATTERNS = {
    # HIPAA Protected Health Information (PHI) - 18 Identifiers
    'SSN': {
        'pattern': r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
        'description': 'Social Security Number (HIPAA PHI #7)',
        'severity': 'CRITICAL',
        'regulations': ['HIPAA', 'CCPA', 'GDPR']
    },
    'CREDIT_CARD': {
        'pattern': r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
        'description': 'Credit Card Number (CCPA Financial Account)',
        'severity': 'CRITICAL',
        'regulations': ['CCPA', 'GDPR']
    },
    'EMAIL': {
        'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'description': 'Email Address (HIPAA PHI #6)',
        'severity': 'HIGH',
        'regulations': ['HIPAA', 'CCPA', 'GDPR']
    },
    'PHONE': {
        'pattern': r'\b(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        'description': 'Phone Number (HIPAA PHI #4)',
        'severity': 'HIGH',
        'regulations': ['HIPAA', 'CCPA', 'GDPR']
    },
    'FAX': {
        'pattern': r'\b(?:fax|facsimile)[\s:]*(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        'description': 'Fax Number (HIPAA PHI #5)',
        'severity': 'HIGH',
        'regulations': ['HIPAA']
    },
    'US_PASSPORT': {
        'pattern': r'\b[A-Z]{1,2}[0-9]{6,9}\b',
        'description': 'US Passport Number (CCPA)',
        'severity': 'CRITICAL',
        'regulations': ['CCPA', 'GDPR']
    },
    'DRIVERS_LICENSE': {
        'pattern': r'\b[A-Z]{1,2}[0-9]{4,8}\b',
        'description': 'Driver License Number (CCPA)',
        'severity': 'CRITICAL',
        'regulations': ['CCPA', 'GDPR']
    },
    'DATE_OF_BIRTH': {
        'pattern': r'\b(?:0[1-9]|1[0-2])[\/\-.](?:0[1-9]|[12]\d|3[01])[\/\-.](?:19|20)\d{2}\b',
        'description': 'Date of Birth (HIPAA PHI #3)',
        'severity': 'CRITICAL',
        'regulations': ['HIPAA', 'CCPA', 'GDPR']
    },
    'MEDICAL_RECORD_NUMBER': {
        'pattern': r'\b(?:MRN|MR|MEDICAL[\s_]?RECORD)[\s:]*[A-Z0-9]{6,12}\b',
        'description': 'Medical Record Number (HIPAA PHI #8)',
        'severity': 'CRITICAL',
        'regulations': ['HIPAA']
    },
    'HEALTH_PLAN_NUMBER': {
        'pattern': r'\b(?:PLAN|POLICY|MEMBER)[\s_#:]*[A-Z0-9]{6,15}\b',
        'description': 'Health Plan Beneficiary Number (HIPAA PHI #9)',
        'severity': 'CRITICAL',
        'regulations': ['HIPAA']
    },
    'ACCOUNT_NUMBER': {
        'pattern': r'\b(?:ACCOUNT|ACCT)[\s_#:]*[A-Z0-9]{6,20}\b',
        'description': 'Account Number (HIPAA PHI #10)',
        'severity': 'HIGH',
        'regulations': ['HIPAA', 'CCPA']
    },
    'CERTIFICATE_LICENSE': {
        'pattern': r'\b(?:CERT|LICENSE|LIC)[\s_#:]*[A-Z0-9]{5,15}\b',
        'description': 'Certificate/License Number (HIPAA PHI #11)',
        'severity': 'HIGH',
        'regulations': ['HIPAA', 'CCPA']
    },
    'VEHICLE_IDENTIFIER': {
        'pattern': r'\b[A-Z0-9]{17}\b|(?:PLATE|LICENSE)[\s_#:]*[A-Z0-9]{2,8}\b',
        'description': 'Vehicle/License Plate Number (HIPAA PHI #12)',
        'severity': 'MEDIUM',
        'regulations': ['HIPAA', 'CCPA', 'GDPR']
    },
    'DEVICE_IDENTIFIER': {
        'pattern': r'\b(?:DEVICE|SERIAL)[\s_#:]*[A-Z0-9]{6,20}\b',
        'description': 'Device Identifier/Serial Number (HIPAA PHI #13)',
        'severity': 'MEDIUM',
        'regulations': ['HIPAA', 'GDPR']
    },
    'URL': {
        'pattern': r'\bhttps?://[A-Za-z0-9.-]+(?:/[A-Za-z0-9._~:/?#[\]@!$&\'()*+,;=-]*)?',
        'description': 'Web URL (HIPAA PHI #14)',
        'severity': 'MEDIUM',
        'regulations': ['HIPAA', 'GDPR']
    },
    'IP_ADDRESS': {
        'pattern': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        'description': 'IP Address (HIPAA PHI #15)',
        'severity': 'MEDIUM',
        'regulations': ['HIPAA', 'CCPA', 'GDPR']
    },
    'BIOMETRIC': {
        'pattern': r'\b(?:FINGERPRINT|VOICEPRINT|RETINA|IRIS|BIOMETRIC)[\s_:]*[A-Z0-9]{10,}\b',
        'description': 'Biometric Identifier (HIPAA PHI #16)',
        'severity': 'CRITICAL',
        'regulations': ['HIPAA', 'CCPA', 'GDPR']
    },
    'ADDRESS': {
        'pattern': r'\b\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd|Court|Ct|Circle|Cir)\b',
        'description': 'Street Address (HIPAA PHI #2)',
        'severity': 'HIGH',
        'regulations': ['HIPAA', 'CCPA', 'GDPR']
    },
    'ZIP_CODE': {
        'pattern': r'\b\d{5}(?:-\d{4})?\b',
        'description': 'ZIP Code (HIPAA PHI #2)',
        'severity': 'MEDIUM',
        'regulations': ['HIPAA', 'CCPA', 'GDPR']
    },
    # GDPR Special Categories
    'RACIAL_ETHNIC_ORIGIN': {
        'pattern': r'\b(?:race|ethnicity|ethnic|racial|ancestry|heritage)[\s:]*[A-Za-z\s]+\b',
        'description': 'Racial or Ethnic Origin (GDPR Special Category)',
        'severity': 'CRITICAL',
        'regulations': ['GDPR', 'CCPA']
    },
    'POLITICAL_OPINION': {
        'pattern': r'\b(?:political|party|democrat|republican|liberal|conservative|political[\s_]?affiliation)[\s:]*[A-Za-z\s]+\b',
        'description': 'Political Opinion (GDPR Special Category)',
        'severity': 'HIGH',
        'regulations': ['GDPR']
    },
    'RELIGIOUS_BELIEF': {
        'pattern': r'\b(?:religion|religious|faith|belief|church|christian|muslim|jewish|hindu|buddhist)[\s:]*[A-Za-z\s]+\b',
        'description': 'Religious Belief (GDPR Special Category)',
        'severity': 'HIGH',
        'regulations': ['GDPR', 'CCPA']
    },
    'TRADE_UNION': {
        'pattern': r'\b(?:union|trade[\s_]?union|labor[\s_]?union|membership)[\s:]*[A-Za-z\s]+\b',
        'description': 'Trade Union Membership (GDPR Special Category)',
        'severity': 'HIGH',
        'regulations': ['GDPR', 'CCPA']
    },
    'GENETIC_DATA': {
        'pattern': r'\b(?:DNA|genetic|genome|chromosome|gene|hereditary)[\s_]*[A-Z0-9]{6,}\b',
        'description': 'Genetic Data (GDPR Special Category)',
        'severity': 'CRITICAL',
        'regulations': ['GDPR', 'HIPAA']
    },
    'HEALTH_DATA': {
        'pattern': r'\b(?:diagnosis|medical|health|condition|disease|illness|treatment|medication|prescription)[\s:]*[A-Za-z0-9\s]+\b',
        'description': 'Health Data (GDPR Special Category)',
        'severity': 'CRITICAL',
        'regulations': ['GDPR', 'HIPAA']
    },
    'SEXUAL_ORIENTATION': {
        'pattern': r'\b(?:sexual[\s_]?orientation|sexuality|gay|lesbian|straight|heterosexual|homosexual|bisexual)[\s:]*[A-Za-z\s]*\b',
        'description': 'Sexual Orientation (GDPR Special Category)',
        'severity': 'CRITICAL',
        'regulations': ['GDPR', 'CCPA']
    },
    # CCPA Additional Categories
    'GEOLOCATION': {
        'pattern': r'\b(?:lat|latitude|lon|longitude|coordinates?)[\s:]*[-+]?\d{1,3}\.\d+,?\s*[-+]?\d{1,3}\.\d+\b',
        'description': 'Precise Geolocation (CCPA)',
        'severity': 'HIGH',
        'regulations': ['CCPA', 'GDPR']
    },
    'IMMIGRATION_STATUS': {
        'pattern': r'\b(?:citizen|citizenship|immigration|visa|green[\s_]?card|resident|alien)[\s:]*[A-Za-z0-9\s]+\b',
        'description': 'Citizenship/Immigration Status (CCPA)',
        'severity': 'HIGH',
        'regulations': ['CCPA', 'GDPR']
    },
    # Common PII Patterns
    'FULL_NAME': {
        'pattern': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',
        'description': 'Full Name (HIPAA PHI #1)',
        'severity': 'HIGH',
        'regulations': ['HIPAA', 'CCPA', 'GDPR']
    },
    'BANK_ACCOUNT': {
        'pattern': r'\b(?:routing|account|aba)[\s_#:]*\d{8,17}\b',
        'description': 'Bank Account/Routing Number',
        'severity': 'CRITICAL',
        'regulations': ['CCPA', 'GDPR']
    }
}

# Column name patterns that might contain PII - Enhanced with regulatory compliance
PII_COLUMN_INDICATORS = [
    # HIPAA PHI Identifiers
    'ssn', 'social_security', 'social_security_number', 'social_sec_num',
    'email', 'email_address', 'e_mail', 'email_addr',
    'phone', 'phone_number', 'telephone', 'mobile', 'cell', 'tel_num',
    'fax', 'fax_number', 'facsimile',
    'medical_record', 'mrn', 'medical_rec_num', 'patient_id',
    'health_plan', 'plan_number', 'beneficiary', 'member_id', 'policy_num',
    'account', 'account_number', 'acct_num', 'account_id',
    'certificate', 'license', 'cert_num', 'license_num', 'lic_num',
    'vehicle', 'vin', 'license_plate', 'plate_number', 'vehicle_id',
    'device', 'serial', 'device_id', 'serial_number', 'device_serial',
    'url', 'web_url', 'website', 'web_address',
    'ip_address', 'ip_addr', 'internet_protocol',
    'biometric', 'fingerprint', 'voiceprint', 'retina', 'iris',
    
    # Names and Personal Identifiers
    'first_name', 'last_name', 'full_name', 'name', 'given_name', 'family_name',
    'middle_name', 'surname', 'maiden_name', 'nickname', 'display_name',
    
    # Address Information
    'address', 'street', 'street_address', 'addr', 'home_address',
    'mailing_address', 'billing_address', 'shipping_address',
    'city', 'state', 'zip', 'zip_code', 'postal_code', 'zipcode',
    'county', 'country', 'region', 'province',
    
    # Financial Information
    'credit_card', 'creditcard', 'cc_number', 'card_number',
    'bank_account', 'routing_number', 'aba_number', 'swift_code',
    'iban', 'account_balance', 'salary', 'income', 'wage',
    
    # Dates
    'birth_date', 'dob', 'date_of_birth', 'birthdate',
    'admission_date', 'discharge_date', 'death_date',
    'hire_date', 'termination_date', 'anniversary_date',
    
    # Government IDs
    'passport', 'passport_number', 'passport_num',
    'driver_license', 'dl_number', 'drivers_license',
    'national_id', 'citizen_id', 'tax_id', 'taxpayer_id',
    'visa_number', 'green_card', 'immigration_status',
    
    # GDPR Special Categories
    'race', 'ethnicity', 'ethnic', 'racial', 'ancestry', 'heritage',
    'political', 'party', 'political_affiliation', 'political_view',
    'religion', 'religious', 'faith', 'belief', 'church',
    'union', 'trade_union', 'labor_union', 'membership',
    'genetic', 'dna', 'genome', 'chromosome', 'gene',
    'health', 'medical', 'diagnosis', 'condition', 'disease',
    'illness', 'treatment', 'medication', 'prescription',
    'sexual_orientation', 'sexuality', 'sex_life',
    
    # Location and Tracking
    'latitude', 'longitude', 'coordinates', 'geolocation',
    'gps', 'location', 'position', 'address_coordinates',
    
    # Biometric and Physical
    'height', 'weight', 'blood_type', 'eye_color', 'hair_color',
    'physical_description', 'distinguishing_marks', 'tattoos', 'scars',
    
    # Employment and Education
    'employee_id', 'emp_id', 'badge_number', 'payroll_id',
    'student_id', 'student_number', 'grade', 'gpa',
    'degree', 'education', 'school', 'university',
    
    # Family and Relationships
    'spouse', 'partner', 'next_of_kin', 'emergency_contact',
    'parent', 'guardian', 'child', 'dependent',
    'marital_status', 'relationship_status',
    
    # Digital Identifiers
    'username', 'user_id', 'login', 'password', 'pin',
    'token', 'session_id', 'cookie', 'tracking_id',
    'device_fingerprint', 'browser_fingerprint',
    
    # Communication
    'message', 'chat', 'conversation', 'email_content',
    'text_message', 'sms', 'communication', 'correspondence'
]

# Scanning configuration
SCAN_CONFIG = {
    'max_rows_to_scan': 10000,  # Maximum rows to scan per table
    'sample_size': 100,         # Sample size for initial analysis
    'confidence_threshold': 0.7  # Minimum confidence for PII detection
}

# Anonymization templates
ANONYMIZATION_TEMPLATES = {
    'SSN': 'XXX-XX-{last4}',
    'CREDIT_CARD': 'XXXX-XXXX-XXXX-{last4}',
    'EMAIL': '{first_letter}***@{domain}',
    'PHONE': 'XXX-XXX-{last4}',
    'NAME': '{first_letter}***'
}
