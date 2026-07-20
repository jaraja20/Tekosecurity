#!/usr/bin/env python3
"""
TEKOSECURE - Encriptación de Credenciales
Protege contraseñas con encriptación AES-256
"""

from cryptography.fernet import Fernet
import base64
import hashlib
import os

class CredentialManager:
    def __init__(self, master_password):
        """Inicializa con master password"""
        self.master_password = master_password
        self.cipher_suite = self._generate_cipher()

    def _generate_cipher(self):
        """Genera cipher a partir de master password"""
        # Convierte master password a clave de 32 bytes
        hash_obj = hashlib.sha256(self.master_password.encode())
        key = base64.urlsafe_b64encode(hash_obj.digest())
        return Fernet(key)

    def encrypt_password(self, password):
        """Encripta una contraseña"""
        encrypted = self.cipher_suite.encrypt(password.encode())
        return encrypted.decode()

    def decrypt_password(self, encrypted_password):
        """Desencripta una contraseña"""
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_password.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"Error desencriptando: {e}")
            return None

    def create_env_file(self, credentials):
        """Crea archivo .env con credenciales encriptadas"""
        env_content = "# TEKOSECURE - Credenciales Encriptadas\n"
        env_content += "# NO COMPARTIR ESTE ARCHIVO\n\n"

        for key, value in credentials.items():
            encrypted = self.encrypt_password(value)
            env_content += f"{key}={encrypted}\n"

        with open('.env', 'w') as f:
            f.write(env_content)

        # Proteger archivo
        os.chmod('.env', 0o600)  # Solo lectura/escritura para propietario
        print("✓ Archivo .env creado (solo lectura)")

if __name__ == "__main__":
    # Master password
    MASTER_PASSWORD = "NasserTi73491654"

    # Credenciales a encriptar
    credentials = {
        "MIKROTIK_PASSWORD": "NasserTi73491654"
    }

    # Crear manager
    manager = CredentialManager(MASTER_PASSWORD)

    # Encriptar y guardar en .env
    manager.create_env_file(credentials)

    print("\n✓ Credenciales encriptadas exitosamente")
    print("✓ Archivo: .env (PROTEGIDO)")
    print("\nPara usar en scripts:")
    print("  from dotenv import load_dotenv")
    print("  from encrypt_credentials import CredentialManager")
    print("  manager = CredentialManager(MASTER_PASSWORD)")
    print("  password = manager.decrypt_password(encrypted_value)")
