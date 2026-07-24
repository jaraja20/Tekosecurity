"""
Secrets Manager - Gestión segura de credenciales
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import json

class SecretsManager:
    """Gestor seguro de secretos con cifrado Fernet"""

    def __init__(self, master_key: str = None):
        """
        Inicializar con master key
        En producción: usar variable de entorno TEKOSECURE_MASTER_KEY
        """
        if not master_key:
            master_key = os.environ.get("TEKOSECURE_MASTER_KEY")
            if not master_key:
                raise ValueError("TEKOSECURE_MASTER_KEY environment variable not set")

        # Derivar clave Fernet desde master key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"tekosecure-salt-2024",  # Fixed salt para consistencia
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.cipher = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Cifrar un secreto"""
        encrypted = self.cipher.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, ciphertext: str) -> str:
        """Desciifrar un secreto"""
        try:
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt secret: {e}")

    def encrypt_config(self, config_dict: dict) -> dict:
        """Cifrar todo un diccionario de configuración"""
        encrypted = {}
        for key, value in config_dict.items():
            if isinstance(value, str) and key in ["password", "secret_key", "token"]:
                encrypted[key] = f"ENCRYPTED[{self.encrypt(value)}]"
            else:
                encrypted[key] = value
        return encrypted

    def decrypt_config(self, config_dict: dict) -> dict:
        """Desciifrar un diccionario de configuración"""
        decrypted = {}
        for key, value in config_dict.items():
            if isinstance(value, str) and value.startswith("ENCRYPTED[") and value.endswith("]"):
                encrypted_part = value[10:-1]  # Remove ENCRYPTED[ and ]
                decrypted[key] = self.decrypt(encrypted_part)
            else:
                decrypted[key] = value
        return decrypted

# Singleton
_manager = None

def get_secrets_manager() -> SecretsManager:
    """Obtener instancia global del gestor de secretos"""
    global _manager
    if _manager is None:
        _manager = SecretsManager()
    return _manager

# Funciones helper
def encrypt_secret(plaintext: str) -> str:
    """Cifrar un secreto"""
    return get_secrets_manager().encrypt(plaintext)

def decrypt_secret(ciphertext: str) -> str:
    """Desciifrar un secreto"""
    return get_secrets_manager().decrypt(ciphertext)
