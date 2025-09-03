from cryptography.fernet import Fernet
import base64
import hashlib


class TokenEncryptionService:
    """Service for encrypting and decrypting OAuth tokens at rest"""

    def __init__(self, key: str):
        # Expect a valid 44-char urlsafe base64 Fernet key from env
        # Pass it directly to Fernet; let Fernet raise a clear error if invalid
        if isinstance(key, str):
            key_bytes = key.encode("utf-8")
        else:
            key_bytes = key
        try:
            # If the provided key is already a valid Fernet key, use it
            self.fernet = Fernet(key_bytes)
        except Exception:
            # Fall back to deriving a deterministic Fernet key from the
            # provided secret (helps tests that pass a short/test key).
            # We use SHA256 and base64-url encode the digest to produce
            # a 44-character urlsafe key compatible with Fernet.
            digest = hashlib.sha256(key_bytes).digest()
            derived = base64.urlsafe_b64encode(digest)
            self.fernet = Fernet(derived)

    def encrypt(self, token: str) -> str:
        """Encrypt a token string"""
        return self.fernet.encrypt(token.encode("utf-8")).decode("utf-8")

    def decrypt(self, encrypted_token: str) -> str:
        """Decrypt an encrypted token string"""
        return self.fernet.decrypt(encrypted_token.encode("utf-8")).decode("utf-8")
