import os
from cryptography.fernet import Fernet
from decouple import config

class EncryptionService:
    _fernet = None

    @classmethod
    def get_fernet(cls):
        if cls._fernet is None:
            key = config("AES_ENCRYPTION_KEY", default=None)
            if not key:
                # Fallback for local dev if forgotten in .env
                key = Fernet.generate_key().decode('utf-8')
            cls._fernet = Fernet(key.encode('utf-8'))
        return cls._fernet

    @classmethod
    def encrypt_file(cls, file_bytes: bytes) -> bytes:
        return cls.get_fernet().encrypt(file_bytes)

    @classmethod
    def decrypt_file(cls, encrypted_bytes: bytes) -> bytes:
        return cls.get_fernet().decrypt(encrypted_bytes)
