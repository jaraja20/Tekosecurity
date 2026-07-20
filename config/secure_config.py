#!/usr/bin/env python3
"""
TEKOSECURE - Gestor de Configuración Segura
Carga credenciales encriptadas desde .env
"""

from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64
import hashlib
import json
import os

# Cargar variables de entorno desde la carpeta config
config_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(config_dir, '.env')
load_dotenv(env_path)

if not os.path.exists(env_path):
    print(f"ADVERTENCIA: Archivo .env no encontrado en {env_path}")

class SecureConfigManager:
    def __init__(self):
        self.master_password = os.getenv('MASTER_PASSWORD')
        self.cipher_suite = self._generate_cipher()
        self.config = self._load_config()

    def _generate_cipher(self):
        """Genera cipher a partir de master password"""
        hash_obj = hashlib.sha256(self.master_password.encode())
        key = base64.urlsafe_b64encode(hash_obj.digest())
        return Fernet(key)

    def _load_config(self):
        """Carga configuración base"""
        config_file = os.path.join(os.path.dirname(__file__), 'network_config.json')
        with open(config_file) as f:
            return json.load(f)

    def get_mikrotik_credentials(self):
        """Obtiene credenciales desencriptadas de Mikrotik"""
        encrypted_password = os.getenv('MIKROTIK_PASSWORD')

        try:
            decrypted = self.cipher_suite.decrypt(encrypted_password.encode()).decode()

            credentials = {
                'ip': self.config['mikrotik']['ip'],
                'port': self.config['mikrotik']['port'],
                'username': self.config['mikrotik']['username'],
                'password': decrypted,
                'ssh_enabled': self.config['mikrotik']['ssh_enabled'],
                'mac_algorithm': self.config['mikrotik']['mac_algorithm']
            }
            return credentials
        except Exception as e:
            print(f"ERROR: No se pudo desencriptar contraseña: {e}")
            return None

    def get_config(self):
        """Obtiene configuración completa"""
        return self.config

    def get_alert_thresholds(self):
        """Obtiene umbrales de alerta"""
        return self.config.get('alert_thresholds', {})

if __name__ == "__main__":
    manager = SecureConfigManager()

    # Prueba
    print("✓ Configuración segura cargada")
    print("\nCredenciales Mikrotik (DESENCRIPTADAS):")
    creds = manager.get_mikrotik_credentials()
    if creds:
        print(f"  IP: {creds['ip']}")
        print(f"  Usuario: {creds['username']}")
        print(f"  Contraseña: {'*' * len(creds['password'])}")
        print(f"  Puerto: {creds['port']}")
