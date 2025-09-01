from cryptography.fernet import Fernet
import base64


class TokenEncryptionService:
    """Service for encrypting and decrypting OAuth tokens at rest"""

    def __init__(self, key: str):
        # Ensure the key is properly formatted for Fernet
        if len(key) < 32:
            # Pad the key if it's too short
            key = key.ljust(32)[:32].encode('utf-8')
            # Base64 encode it to make it valid for Fernet
            key = base64.urlsafe_b64encode(key)
        else:
            # If the key is long enough, just base64 encode it
            key = base64.urlsafe_b64encode(key.encode('utf-8'))

        self.fernet = Fernet(key)

    def encrypt(self, token: str) -> str:
        """Encrypt a token string"""
        return self.fernet.encrypt(token.encode('utf-8')).decode('utf-8')

    def decrypt(self, encrypted_token: str) -> str:
        """Decrypt an encrypted token string"""
        return self.fernet.decrypt(encrypted_token.encode('utf-8')).decode('utf-8')
