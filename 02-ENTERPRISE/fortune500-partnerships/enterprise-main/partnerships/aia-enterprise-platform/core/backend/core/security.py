"""
AIA Enterprise Platform - Security Manager
=========================================

Production-grade security implementation with JWT authentication,
encryption, input validation, and enterprise security features.
"""

import os
import jwt
import bcrypt
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import logging

from aia.aia-enterprise-platform.core.backend.core..config.settings import settings

logger = logging.getLogger(__name__)


class SecurityManager:
    """Comprehensive security management for the AIA Enterprise Platform"""

    def __init__(self):
        self.jwt_algorithm = settings.jwt_algorithm
        self.jwt_expiration_hours = settings.jwt_expiration_hours
        self.secret_key = settings.secret_key
        self.encrypt_key = settings.encrypt_key
        self.cipher_suite = None
        self.initialized = False

    async def initialize(self):
        """Initialize security components"""
        try:
            # Initialize encryption if key is provided
            if self.encrypt_key:
                self.cipher_suite = Fernet(self.encrypt_key.encode()[:44].ljust(44, b'='))
            else:
                # Generate encryption key if not provided (development only)
                if settings.is_development:
                    key = Fernet.generate_key()
                    self.cipher_suite = Fernet(key)
                    logger.warning("Generated temporary encryption key for development")

            self.initialized = True
            logger.info("🛡️ Security manager initialized successfully")

        except Exception as e:
            logger.error(f"Security manager initialization failed: {e}")
            raise

    def generate_token(self, user_data: Dict[str, Any], expires_in_hours: Optional[int] = None) -> str:
        """Generate JWT token for user authentication"""
        if not self.initialized:
            raise RuntimeError("Security manager not initialized")

        expiration_hours = expires_in_hours or self.jwt_expiration_hours
        expiration = datetime.utcnow() + timedelta(hours=expiration_hours)

        payload = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "role": user_data.get("role", "user"),
            "permissions": user_data.get("permissions", []),
            "iat": datetime.utcnow(),
            "exp": expiration,
            "iss": "aia-enterprise-platform",
            "aud": "aia-users"
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.jwt_algorithm)
        return token

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        if not self.initialized:
            raise RuntimeError("Security manager not initialized")

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.jwt_algorithm],
                audience="aia-users",
                issuer="aia-enterprise-platform"
            )

            # Check token expiration
            if payload.get("exp") and datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
                raise jwt.ExpiredSignatureError("Token has expired")

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self.cipher_suite:
            raise RuntimeError("Encryption not available")

        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Data encryption error: {e}")
            raise ValueError("Encryption failed")

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self.cipher_suite:
            raise RuntimeError("Encryption not available")

        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Data decryption error: {e}")
            raise ValueError("Decryption failed")

    def generate_api_key(self, length: int = 32) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(length)

    def generate_secure_hash(self, data: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Generate secure hash with salt"""
        if salt is None:
            salt = secrets.token_hex(16)

        hash_object = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
        secure_hash = base64.b64encode(hash_object).decode()

        return secure_hash, salt

    def verify_secure_hash(self, data: str, hash_value: str, salt: str) -> bool:
        """Verify data against secure hash"""
        try:
            computed_hash, _ = self.generate_secure_hash(data, salt)
            return hmac.compare_digest(computed_hash, hash_value)
        except Exception as e:
            logger.error(f"Hash verification error: {e}")
            return False

    def validate_input(self, input_data: Any, validation_rules: Dict[str, Any]) -> bool:
        """Validate input data against security rules"""
        if not isinstance(input_data, dict):
            return False

        for field, rules in validation_rules.items():
            value = input_data.get(field)

            # Check required fields
            if rules.get("required", False) and value is None:
                logger.warning(f"Required field missing: {field}")
                return False

            # Check data types
            if value is not None and "type" in rules:
                expected_type = rules["type"]
                if not isinstance(value, expected_type):
                    logger.warning(f"Invalid type for field {field}: expected {expected_type}, got {type(value)}")
                    return False

            # Check string length
            if isinstance(value, str) and "max_length" in rules:
                if len(value) > rules["max_length"]:
                    logger.warning(f"Field {field} exceeds maximum length: {len(value)} > {rules['max_length']}")
                    return False

            # Check for dangerous patterns
            if isinstance(value, str) and self._contains_dangerous_patterns(value):
                logger.warning(f"Dangerous pattern detected in field {field}")
                return False

        return True

    def _contains_dangerous_patterns(self, value: str) -> bool:
        """Check for dangerous patterns in input"""
        dangerous_patterns = [
            # SQL injection patterns
            r"(?i)(union|select|insert|update|delete|drop|create|alter)\s",
            r"(?i)(exec|execute|sp_|xp_)",
            r"['\";]",

            # XSS patterns
            r"<script",
            r"javascript:",
            r"onload=",
            r"onerror=",

            # Command injection patterns
            r"[;&|`$()]",
            r"(?i)(rm\s|del\s|format\s)",

            # Path traversal
            r"\.\./",
            r"\\\.\.\\",
        ]

        import re
        for pattern in dangerous_patterns:
            if re.search(pattern, value):
                return True

        return False

    def sanitize_input(self, input_data: str) -> str:
        """Sanitize input data"""
        if not isinstance(input_data, str):
            return input_data

        # Remove or escape dangerous characters
        sanitized = input_data.replace("<", "&lt;").replace(">", "&gt;")
        sanitized = sanitized.replace("'", "&#39;").replace('"', "&quot;")
        sanitized = sanitized.replace("&", "&amp;")

        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')

        return sanitized

    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        data = f"{session_id}:{timestamp}"
        token_hash = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{timestamp}.{token_hash}"

    def verify_csrf_token(self, token: str, session_id: str, max_age: int = 3600) -> bool:
        """Verify CSRF token"""
        try:
            timestamp_str, token_hash = token.split('.', 1)
            timestamp = int(timestamp_str)

            # Check token age
            if datetime.utcnow().timestamp() - timestamp > max_age:
                logger.warning("CSRF token expired")
                return False

            # Verify token
            expected_data = f"{session_id}:{timestamp_str}"
            expected_hash = hmac.new(
                self.secret_key.encode(),
                expected_data.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(token_hash, expected_hash)

        except (ValueError, AttributeError) as e:
            logger.warning(f"Invalid CSRF token format: {e}")
            return False

    def check_permission(self, user_permissions: List[str], required_permission: str) -> bool:
        """Check if user has required permission"""
        if "admin" in user_permissions:
            return True  # Admin has all permissions

        return required_permission in user_permissions

    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' wss: https:; "
                "frame-ancestors 'none'"
            ),
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "accelerometer=()"
            )
        }

    def audit_log_security_event(self, event_type: str, user_id: Optional[str] = None,
                                details: Optional[Dict[str, Any]] = None):
        """Log security-related events for audit purposes"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details or {},
            "severity": self._get_event_severity(event_type)
        }

        # In production, this should be sent to a secure logging service
        if settings.is_production:
            logger.warning(f"SECURITY_AUDIT: {audit_entry}")
        else:
            logger.info(f"Security audit: {audit_entry}")

    def _get_event_severity(self, event_type: str) -> str:
        """Get severity level for security event"""
        high_severity_events = [
            "authentication_failure",
            "authorization_failure",
            "token_tampering",
            "suspicious_activity",
            "data_breach_attempt"
        ]

        medium_severity_events = [
            "login_attempt",
            "password_change",
            "permission_check_failed"
        ]

        if event_type in high_severity_events:
            return "HIGH"
        elif event_type in medium_severity_events:
            return "MEDIUM"
        else:
            return "LOW"


# Global security manager instance
security_manager = SecurityManager()