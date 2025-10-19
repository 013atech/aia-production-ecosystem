"""
Enterprise Secrets Management System
===================================
Date: 2025-09-18
Purpose: Comprehensive secrets management with rotation policies and secure storage
"""

import os
import secrets
import hashlib
import hmac
import json
import asyncio
from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa
import base64
import logging
from enum import Enum
import aiofiles

logger = logging.getLogger(__name__)

class SecretType(Enum):
    """Types of secrets managed by the system"""
    JWT_KEY = "jwt_key"
    API_KEY = "api_key"
    DATABASE_PASSWORD = "database_password"
    ENCRYPTION_KEY = "encryption_key"
    EXTERNAL_API_KEY = "external_api_key"
    SESSION_SECRET = "session_secret"
    OAUTH_SECRET = "oauth_secret"

class SecretRotationPolicy(Enum):
    """Secret rotation policies"""
    NEVER = "never"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class SecretMetadata:
    """Metadata for a managed secret"""
    def __init__(
        self,
        secret_id: str,
        secret_type: SecretType,
        rotation_policy: SecretRotationPolicy,
        created_at: datetime = None,
        last_rotated: datetime = None,
        rotation_count: int = 0,
        is_active: bool = True
    ):
        self.secret_id = secret_id
        self.secret_type = secret_type
        self.rotation_policy = rotation_policy
        self.created_at = created_at or datetime.utcnow()
        self.last_rotated = last_rotated or self.created_at
        self.rotation_count = rotation_count
        self.is_active = is_active

    def needs_rotation(self) -> bool:
        """Check if secret needs rotation based on policy"""
        if self.rotation_policy == SecretRotationPolicy.NEVER:
            return False

        now = datetime.utcnow()
        time_since_rotation = now - self.last_rotated

        rotation_intervals = {
            SecretRotationPolicy.DAILY: timedelta(days=1),
            SecretRotationPolicy.WEEKLY: timedelta(days=7),
            SecretRotationPolicy.MONTHLY: timedelta(days=30),
            SecretRotationPolicy.QUARTERLY: timedelta(days=90),
            SecretRotationPolicy.YEARLY: timedelta(days=365),
        }

        threshold = rotation_intervals.get(self.rotation_policy)
        if threshold:
            return time_since_rotation >= threshold

        return False

class EnterpriseSecretsManager:
    """Enterprise-grade secrets manager with rotation and secure storage"""

    def __init__(self, master_key: Optional[str] = None, storage_path: str = "secrets/"):
        self.storage_path = storage_path
        self.secrets_cache: Dict[str, str] = {}
        self.metadata_cache: Dict[str, SecretMetadata] = {}

        # Initialize master key for encryption
        if master_key:
            self.master_key = master_key.encode()
        else:
            self.master_key = self._generate_or_load_master_key()

        self.cipher_suite = self._create_cipher()
        self.initialized = False

    def _generate_or_load_master_key(self) -> bytes:
        """Generate or load the master encryption key"""
        master_key_path = os.path.join(self.storage_path, ".master_key")

        if os.path.exists(master_key_path):
            try:
                with open(master_key_path, "rb") as f:
                    return base64.urlsafe_b64decode(f.read())
            except Exception as e:
                logger.error(f"Failed to load master key: {e}")

        # Generate new master key
        master_key = secrets.token_bytes(32)  # 256-bit key

        try:
            os.makedirs(self.storage_path, mode=0o700, exist_ok=True)
            with open(master_key_path, "wb") as f:
                f.write(base64.urlsafe_b64encode(master_key))
            os.chmod(master_key_path, 0o600)
            logger.info("Generated new master key for secrets encryption")
        except Exception as e:
            logger.error(f"Failed to save master key: {e}")

        return master_key

    def _create_cipher(self) -> Fernet:
        """Create Fernet cipher for symmetric encryption"""
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"aia_secrets_salt_2024",  # Use consistent salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return Fernet(key)

    async def initialize(self):
        """Initialize the secrets manager"""
        if self.initialized:
            return

        try:
            os.makedirs(self.storage_path, mode=0o700, exist_ok=True)
            await self._load_existing_secrets()
            self.initialized = True
            logger.info("Enterprise Secrets Manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize secrets manager: {e}")
            raise

    async def _load_existing_secrets(self):
        """Load existing secrets and metadata from storage"""
        metadata_path = os.path.join(self.storage_path, "metadata.json")

        if os.path.exists(metadata_path):
            try:
                async with aiofiles.open(metadata_path, "r") as f:
                    content = await f.read()
                    metadata = json.loads(content)

                    for secret_id, meta_data in metadata.items():
                        self.metadata_cache[secret_id] = SecretMetadata(
                            secret_id=meta_data["secret_id"],
                            secret_type=SecretType(meta_data["secret_type"]),
                            rotation_policy=SecretRotationPolicy(meta_data["rotation_policy"]),
                            created_at=datetime.fromisoformat(meta_data["created_at"]),
                            last_rotated=datetime.fromisoformat(meta_data["last_rotated"]),
                            rotation_count=meta_data["rotation_count"],
                            is_active=meta_data["is_active"]
                        )

                logger.info(f"Loaded {len(self.metadata_cache)} secret metadata entries")
            except Exception as e:
                logger.error(f"Failed to load secrets metadata: {e}")

    async def _save_metadata(self):
        """Save secrets metadata to storage"""
        metadata_path = os.path.join(self.storage_path, "metadata.json")

        metadata = {}
        for secret_id, meta in self.metadata_cache.items():
            metadata[secret_id] = {
                "secret_id": meta.secret_id,
                "secret_type": meta.secret_type.value,
                "rotation_policy": meta.rotation_policy.value,
                "created_at": meta.created_at.isoformat(),
                "last_rotated": meta.last_rotated.isoformat(),
                "rotation_count": meta.rotation_count,
                "is_active": meta.is_active
            }

        try:
            async with aiofiles.open(metadata_path, "w") as f:
                await f.write(json.dumps(metadata, indent=2))
            os.chmod(metadata_path, 0o600)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    def generate_secret(self, secret_type: SecretType, length: int = 32) -> str:
        """Generate a cryptographically secure secret"""
        if secret_type == SecretType.JWT_KEY:
            return secrets.token_urlsafe(64)  # 512 bits for JWT
        elif secret_type == SecretType.API_KEY:
            return f"aia_{secrets.token_urlsafe(48)}"
        elif secret_type == SecretType.ENCRYPTION_KEY:
            return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
        elif secret_type == SecretType.DATABASE_PASSWORD:
            # Generate complex password
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
            return ''.join(secrets.choice(chars) for _ in range(length))
        else:
            return secrets.token_urlsafe(length)

    async def store_secret(
        self,
        secret_id: str,
        secret_value: str,
        secret_type: SecretType,
        rotation_policy: SecretRotationPolicy = SecretRotationPolicy.MONTHLY
    ) -> bool:
        """Store a secret securely with metadata"""
        if not self.initialized:
            await self.initialize()

        try:
            # Encrypt the secret
            encrypted_secret = self.cipher_suite.encrypt(secret_value.encode())

            # Store encrypted secret to file
            secret_path = os.path.join(self.storage_path, f"{secret_id}.enc")
            async with aiofiles.open(secret_path, "wb") as f:
                await f.write(encrypted_secret)
            os.chmod(secret_path, 0o600)

            # Update metadata
            self.metadata_cache[secret_id] = SecretMetadata(
                secret_id=secret_id,
                secret_type=secret_type,
                rotation_policy=rotation_policy
            )

            # Cache the secret
            self.secrets_cache[secret_id] = secret_value

            await self._save_metadata()
            logger.info(f"Secret '{secret_id}' stored successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to store secret '{secret_id}': {e}")
            return False

    async def get_secret(self, secret_id: str) -> Optional[str]:
        """Retrieve a secret by ID"""
        if not self.initialized:
            await self.initialize()

        # Check cache first
        if secret_id in self.secrets_cache:
            return self.secrets_cache[secret_id]

        # Load from storage
        try:
            secret_path = os.path.join(self.storage_path, f"{secret_id}.enc")
            if not os.path.exists(secret_path):
                return None

            async with aiofiles.open(secret_path, "rb") as f:
                encrypted_secret = await f.read()

            # Decrypt secret
            decrypted_secret = self.cipher_suite.decrypt(encrypted_secret)
            secret_value = decrypted_secret.decode()

            # Cache it
            self.secrets_cache[secret_id] = secret_value
            return secret_value

        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_id}': {e}")
            return None

    async def rotate_secret(self, secret_id: str) -> bool:
        """Rotate a secret by generating a new value"""
        if not self.initialized:
            await self.initialize()

        metadata = self.metadata_cache.get(secret_id)
        if not metadata:
            logger.error(f"No metadata found for secret '{secret_id}'")
            return False

        try:
            # Generate new secret value
            new_secret = self.generate_secret(metadata.secret_type)

            # Store the new secret
            success = await self.store_secret(
                secret_id=secret_id,
                secret_value=new_secret,
                secret_type=metadata.secret_type,
                rotation_policy=metadata.rotation_policy
            )

            if success:
                # Update metadata
                metadata.last_rotated = datetime.utcnow()
                metadata.rotation_count += 1
                await self._save_metadata()

                logger.info(f"Secret '{secret_id}' rotated successfully (count: {metadata.rotation_count})")
                return True

        except Exception as e:
            logger.error(f"Failed to rotate secret '{secret_id}': {e}")

        return False

    async def check_and_rotate_expired_secrets(self) -> List[str]:
        """Check for expired secrets and rotate them automatically"""
        if not self.initialized:
            await self.initialize()

        rotated_secrets = []

        for secret_id, metadata in self.metadata_cache.items():
            if metadata.is_active and metadata.needs_rotation():
                logger.info(f"Auto-rotating expired secret: {secret_id}")
                if await self.rotate_secret(secret_id):
                    rotated_secrets.append(secret_id)

        return rotated_secrets

    async def delete_secret(self, secret_id: str) -> bool:
        """Securely delete a secret"""
        if not self.initialized:
            await self.initialize()

        try:
            # Remove from cache
            self.secrets_cache.pop(secret_id, None)

            # Remove metadata
            self.metadata_cache.pop(secret_id, None)

            # Remove encrypted file
            secret_path = os.path.join(self.storage_path, f"{secret_id}.enc")
            if os.path.exists(secret_path):
                # Overwrite file with random data before deletion for security
                file_size = os.path.getsize(secret_path)
                with open(secret_path, "wb") as f:
                    f.write(secrets.token_bytes(file_size))
                os.remove(secret_path)

            await self._save_metadata()
            logger.info(f"Secret '{secret_id}' deleted securely")
            return True

        except Exception as e:
            logger.error(f"Failed to delete secret '{secret_id}': {e}")
            return False

    def list_secrets(self) -> List[Dict[str, Any]]:
        """List all managed secrets with their metadata (without values)"""
        secrets_list = []

        for secret_id, metadata in self.metadata_cache.items():
            secrets_list.append({
                "secret_id": secret_id,
                "secret_type": metadata.secret_type.value,
                "rotation_policy": metadata.rotation_policy.value,
                "created_at": metadata.created_at.isoformat(),
                "last_rotated": metadata.last_rotated.isoformat(),
                "rotation_count": metadata.rotation_count,
                "is_active": metadata.is_active,
                "needs_rotation": metadata.needs_rotation()
            })

        return secrets_list

    async def backup_secrets(self, backup_path: str, encryption_password: str) -> bool:
        """Create an encrypted backup of all secrets"""
        try:
            backup_data = {
                "metadata": {},
                "secrets": {}
            }

            # Collect metadata
            for secret_id, metadata in self.metadata_cache.items():
                backup_data["metadata"][secret_id] = {
                    "secret_type": metadata.secret_type.value,
                    "rotation_policy": metadata.rotation_policy.value,
                    "created_at": metadata.created_at.isoformat(),
                    "last_rotated": metadata.last_rotated.isoformat(),
                    "rotation_count": metadata.rotation_count,
                    "is_active": metadata.is_active
                }

            # Collect encrypted secrets
            for secret_id in self.metadata_cache.keys():
                secret_value = await self.get_secret(secret_id)
                if secret_value:
                    backup_data["secrets"][secret_id] = secret_value

            # Encrypt backup with user-provided password
            backup_json = json.dumps(backup_data).encode()

            # Create Fernet key from password
            password_bytes = encryption_password.encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"aia_backup_salt_2024",
                iterations=200000,
            )
            backup_key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            backup_cipher = Fernet(backup_key)

            encrypted_backup = backup_cipher.encrypt(backup_json)

            # Save backup
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            async with aiofiles.open(backup_path, "wb") as f:
                await f.write(encrypted_backup)
            os.chmod(backup_path, 0o600)

            logger.info(f"Secrets backup created: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False

# Global secrets manager instance
secrets_manager: Optional[EnterpriseSecretsManager] = None

async def get_secrets_manager() -> EnterpriseSecretsManager:
    """Get or initialize the global secrets manager"""
    global secrets_manager

    if secrets_manager is None:
        storage_path = os.getenv("SECRETS_STORAGE_PATH", "secrets/")
        master_key = os.getenv("SECRETS_MASTER_KEY")
        secrets_manager = EnterpriseSecretsManager(master_key, storage_path)
        await secrets_manager.initialize()

    return secrets_manager

async def auto_rotate_secrets_task():
    """Background task to automatically rotate expired secrets"""
    while True:
        try:
            manager = await get_secrets_manager()
            rotated = await manager.check_and_rotate_expired_secrets()
            if rotated:
                logger.info(f"Auto-rotated {len(rotated)} expired secrets: {rotated}")

            # Run every hour
            await asyncio.sleep(3600)

        except Exception as e:
            logger.error(f"Error in auto-rotation task: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes before retrying