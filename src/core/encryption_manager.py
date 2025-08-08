"""
Data Encryption and Decryption Utilities
Handles secure encryption/decryption of PII data with key management
"""

import os
import base64
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
from env_config import env_config

class EncryptionManager:
    def __init__(self, master_key_file: Optional[str] = None):
        """Initialize encryption manager with master key"""
        self.master_key_file = master_key_file or env_config.master_key_file
        self.logger = logging.getLogger(__name__)
        self.encryption_keys = {}  # Cache for derived keys
        self._ensure_master_key()
    
    def _ensure_master_key(self):
        """Ensure master key exists, create if needed"""
        if not os.path.exists(self.master_key_file):
            master_key = Fernet.generate_key()
            with open(self.master_key_file, 'wb') as f:
                f.write(master_key)
            self.logger.info("Generated new master encryption key")
            
            # Set restrictive permissions (Unix-like systems)
            try:
                os.chmod(self.master_key_file, 0o600)
            except:
                pass  # Windows doesn't support chmod
        else:
            self.logger.info("Using existing master encryption key")
    
    def _get_master_key(self) -> bytes:
        """Get the master key from file"""
        try:
            with open(self.master_key_file, 'rb') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to read master key: {str(e)}")
            raise
    
    def _derive_key(self, hint: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Derive an encryption key from hint and salt"""
        if salt is None:
            salt = os.urandom(16)
        
        master_key = self._get_master_key()
        
        # Combine master key and hint
        combined = master_key + hint.encode('utf-8')
        
        # Use PBKDF2 to derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=env_config.key_derivation_iterations,
        )
        
        derived_key = base64.urlsafe_b64encode(kdf.derive(combined))
        return derived_key, salt
    
    def encrypt_pii_value(self, value: str, encryption_hint: str) -> Dict[str, Any]:
        """
        Encrypt a PII value with the given encryption hint
        
        Args:
            value: The PII value to encrypt
            encryption_hint: Hint for key derivation (e.g., 'pii_ssn_202508')
        
        Returns:
            Dict with encrypted data and metadata
        """
        try:
            # Derive key from hint
            derived_key, salt = self._derive_key(encryption_hint)
            
            # Create Fernet cipher
            fernet = Fernet(derived_key)
            
            # Encrypt the value
            encrypted_value = fernet.encrypt(value.encode('utf-8'))
            
            # Create metadata
            metadata = {
                'encrypted_data': base64.urlsafe_b64encode(encrypted_value).decode('utf-8'),
                'salt': base64.urlsafe_b64encode(salt).decode('utf-8'),
                'encryption_hint': encryption_hint,
                'encrypted_at': datetime.now().isoformat(),
                'algorithm': 'Fernet',
                'key_derivation': 'PBKDF2-SHA256'
            }
            
            self.logger.debug(f"Encrypted PII value with hint: {encryption_hint}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to encrypt PII value: {str(e)}")
            raise
    
    def decrypt_pii_value(self, encrypted_metadata: Dict[str, Any]) -> str:
        """
        Decrypt a PII value using the stored metadata
        
        Args:
            encrypted_metadata: Dict containing encrypted data and metadata
        
        Returns:
            Decrypted original value
        """
        try:
            # Extract metadata
            encrypted_data = base64.urlsafe_b64decode(encrypted_metadata['encrypted_data'])
            salt = base64.urlsafe_b64decode(encrypted_metadata['salt'])
            encryption_hint = encrypted_metadata['encryption_hint']
            
            # Derive the same key
            derived_key, _ = self._derive_key(encryption_hint, salt)
            
            # Create Fernet cipher
            fernet = Fernet(derived_key)
            
            # Decrypt the value
            decrypted_bytes = fernet.decrypt(encrypted_data)
            decrypted_value = decrypted_bytes.decode('utf-8')
            
            self.logger.debug(f"Decrypted PII value with hint: {encryption_hint}")
            return decrypted_value
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt PII value: {str(e)}")
            raise
    
    def mask_pii_value(self, value: str, pii_type: str, mask_char: str = '*') -> str:
        """
        Mask a PII value for display purposes
        
        Args:
            value: Original PII value
            pii_type: Type of PII (affects masking strategy)
            mask_char: Character to use for masking
        
        Returns:
            Masked value safe for display
        """
        if not value or len(value) == 0:
            return value
        
        try:
            value_str = str(value)
            
            # Different masking strategies based on PII type
            if pii_type in ['SSN', 'SOCIAL_SECURITY_NUMBER']:
                # SSN: Show last 4 digits
                if len(value_str) >= 4:
                    return mask_char * (len(value_str) - 4) + value_str[-4:]
                else:
                    return mask_char * len(value_str)
            
            elif pii_type in ['EMAIL', 'EMAIL_ADDRESS']:
                # Email: Show first letter and domain
                if '@' in value_str:
                    local, domain = value_str.split('@', 1)
                    if len(local) > 0:
                        masked_local = local[0] + mask_char * (len(local) - 1)
                        return f"{masked_local}@{domain}"
                return mask_char * len(value_str)
            
            elif pii_type in ['PHONE', 'PHONE_NUMBER']:
                # Phone: Show last 4 digits
                digits_only = ''.join(filter(str.isdigit, value_str))
                if len(digits_only) >= 4:
                    masked_digits = mask_char * (len(digits_only) - 4) + digits_only[-4:]
                    # Preserve original formatting structure
                    result = ""
                    digit_index = 0
                    for char in value_str:
                        if char.isdigit():
                            result += masked_digits[digit_index]
                            digit_index += 1
                        else:
                            result += char
                    return result
                else:
                    return mask_char * len(value_str)
            
            elif pii_type in ['CREDIT_CARD', 'CREDIT_CARD_NUMBER']:
                # Credit Card: Show last 4 digits
                digits_only = ''.join(filter(str.isdigit, value_str))
                if len(digits_only) >= 4:
                    return mask_char * (len(value_str) - 4) + value_str[-4:]
                else:
                    return mask_char * len(value_str)
            
            elif pii_type in ['FULL_NAME', 'FIRST_NAME', 'LAST_NAME']:
                # Name: Show first letter of each word
                words = value_str.split()
                masked_words = []
                for word in words:
                    if len(word) > 0:
                        masked_words.append(word[0] + mask_char * (len(word) - 1))
                return ' '.join(masked_words)
            
            elif pii_type in ['ADDRESS']:
                # Address: Show first few characters
                if len(value_str) > 10:
                    return value_str[:3] + mask_char * (len(value_str) - 3)
                else:
                    return mask_char * len(value_str)
            
            else:
                # Default: Show first and last character if long enough
                if len(value_str) <= 2:
                    return mask_char * len(value_str)
                elif len(value_str) <= 4:
                    return value_str[0] + mask_char * (len(value_str) - 1)
                else:
                    return value_str[0] + mask_char * (len(value_str) - 2) + value_str[-1]
        
        except Exception as e:
            self.logger.error(f"Failed to mask PII value: {str(e)}")
            return mask_char * len(str(value))
    
    def generate_encryption_hint(self, pii_type: str, context: Dict[str, Any]) -> str:
        """
        Generate an encryption hint for key derivation
        
        Args:
            pii_type: Type of PII being encrypted
            context: Additional context (table, column, etc.)
        
        Returns:
            Encryption hint string
        """
        try:
            # Create hint from PII type, table context, and current month
            components = [
                'pii',
                pii_type.lower(),
                context.get('table_name', 'unknown')[:10],  # Limit length
                datetime.now().strftime('%Y%m')  # Year-month for rotation
            ]
            
            hint = '_'.join(components)
            return hint
            
        except Exception as e:
            self.logger.error(f"Failed to generate encryption hint: {str(e)}")
            return f"pii_{pii_type.lower()}_{datetime.now().strftime('%Y%m')}"
    
    def rotate_keys(self, old_hint_pattern: str, new_hint: str) -> int:
        """
        Rotate encryption keys by re-encrypting data with new keys
        
        Args:
            old_hint_pattern: Pattern to match old encryption hints
            new_hint: New encryption hint to use
        
        Returns:
            Number of records re-encrypted
        """
        # This would require integration with results_manager to find and
        # re-encrypt existing encrypted PII values
        self.logger.warning("Key rotation not yet implemented")
        return 0
    
    def verify_decryption(self, original: str, encrypted_metadata: Dict[str, Any]) -> bool:
        """
        Verify that encryption/decryption works correctly
        
        Args:
            original: Original plaintext value
            encrypted_metadata: Encrypted metadata
        
        Returns:
            True if decryption matches original
        """
        try:
            decrypted = self.decrypt_pii_value(encrypted_metadata)
            return original == decrypted
        except Exception as e:
            self.logger.error(f"Decryption verification failed: {str(e)}")
            return False

class DataProtectionUtils:
    """Utility functions for data protection"""
    
    @staticmethod
    def is_encryption_needed(pii_type: str, confidence: float, context: Dict[str, Any]) -> bool:
        """
        Determine if a PII value should be encrypted based on type and context
        
        Args:
            pii_type: Type of PII detected
            confidence: Detection confidence score
            context: Additional context
        
        Returns:
            True if encryption is recommended
        """
        # High-sensitivity PII types that should always be encrypted
        high_sensitivity = {
            'SSN', 'SOCIAL_SECURITY_NUMBER', 'CREDIT_CARD', 'CREDIT_CARD_NUMBER',
            'MEDICAL_RECORD_NUMBER', 'HEALTH_PLAN_NUMBER', 'BIOMETRIC',
            'GENETIC_DATA', 'HEALTH_DATA', 'FINANCIAL_ACCOUNT'
        }
        
        # Confidence threshold for encryption
        HIGH_CONFIDENCE_THRESHOLD = 0.8
        
        # Always encrypt high-sensitivity PII
        if pii_type in high_sensitivity:
            return True
        
        # Encrypt high-confidence detections of medium-sensitivity PII
        if confidence >= HIGH_CONFIDENCE_THRESHOLD:
            medium_sensitivity = {
                'EMAIL', 'PHONE', 'FULL_NAME', 'ADDRESS', 'DATE_OF_BIRTH',
                'DRIVER_LICENSE', 'PASSPORT', 'IP_ADDRESS'
            }
            if pii_type in medium_sensitivity:
                return True
        
        return False
    
    @staticmethod
    def get_regulatory_requirements(pii_type: str) -> List[str]:
        """
        Get regulatory requirements for a specific PII type
        
        Args:
            pii_type: Type of PII
        
        Returns:
            List of applicable regulations
        """
        regulations = []
        
        # HIPAA PHI identifiers
        hipaa_phi = {
            'FULL_NAME', 'ADDRESS', 'DATE_OF_BIRTH', 'PHONE', 'FAX', 'EMAIL',
            'SSN', 'MEDICAL_RECORD_NUMBER', 'HEALTH_PLAN_NUMBER', 'ACCOUNT_NUMBER',
            'CERTIFICATE_LICENSE', 'VEHICLE_IDENTIFIER', 'DEVICE_IDENTIFIER',
            'URL', 'IP_ADDRESS', 'BIOMETRIC', 'HEALTH_DATA'
        }
        
        # GDPR Special Categories
        gdpr_special = {
            'RACIAL_ETHNIC_ORIGIN', 'POLITICAL_OPINION', 'RELIGIOUS_BELIEF',
            'TRADE_UNION', 'GENETIC_DATA', 'BIOMETRIC', 'HEALTH_DATA',
            'SEXUAL_ORIENTATION'
        }
        
        # CCPA Sensitive Personal Information
        ccpa_sensitive = {
            'SSN', 'DRIVER_LICENSE', 'PASSPORT', 'FINANCIAL_ACCOUNT',
            'GEOLOCATION', 'RACIAL_ETHNIC_ORIGIN', 'RELIGIOUS_BELIEF',
            'TRADE_UNION', 'GENETIC_DATA', 'BIOMETRIC', 'HEALTH_DATA',
            'SEXUAL_ORIENTATION'
        }
        
        if pii_type in hipaa_phi:
            regulations.append('HIPAA')
        if pii_type in gdpr_special:
            regulations.append('GDPR')
        if pii_type in ccpa_sensitive:
            regulations.append('CCPA')
        
        # General data protection applies to most PII
        if pii_type in {'EMAIL', 'PHONE', 'FULL_NAME', 'ADDRESS', 'DATE_OF_BIRTH'}:
            if 'GDPR' not in regulations:
                regulations.append('GDPR')
            if 'CCPA' not in regulations:
                regulations.append('CCPA')
        
        return regulations

# Global encryption manager instance
encryption_manager = EncryptionManager()
data_protection = DataProtectionUtils()
