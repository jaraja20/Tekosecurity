#!/usr/bin/env python3
"""
TEKOSECURE - Monitor Hikvision
Monitorea estado de NVRs y cámaras Hikvision por SNMP/HTTP
"""

import sys
import os
import json
import logging
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

# Agregar ruta de config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))

from secure_config import SecureConfigManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/hikvision_events.log'),
        logging.StreamHandler()
    ]
)

class HikvisionMonitor:
    def __init__(self):
        try:
            self.config_manager = SecureConfigManager()
            with open(os.path.join(os.path.dirname(__file__), '..', 'config', 'hikvision_devices.json')) as f:
                self.devices_config = json.load(f)
            self.session = requests.Session()
            self.session.verify = False  # Deshabilita verificación SSL (equipos locales)
            logging.info(f"Monitor Hikvision inicializado - {len(self.devices_config['hikvision_nvrs'])} NVRs")
        except Exception as e:
            logging.error(f"Error inicializando monitor Hikvision: {e}")
            sys.exit(1)

    def get_password(self, password_key):
        """Obtiene contraseña desencriptada"""
        import os
        from dotenv import load_dotenv

        env_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env')
        load_dotenv(env_path)

        encrypted = os.getenv(password_key)
        if not encrypted:
            return None

        from cryptography.fernet import Fernet
        import base64
        import hashlib

        master_password = os.getenv('MASTER_PASSWORD')
        hash_obj = hashlib.sha256(master_password.encode())
        key = base64.urlsafe_b64encode(hash_obj.digest())
        cipher = Fernet(key)

        try:
            return cipher.decrypt(encrypted.encode()).decode()
        except:
            return None

    def test_connection(self, nvr):
        """Prueba conexión a NVR"""
        try:
            ip = nvr['ip']
            username = nvr['username']
            password_key = nvr['password_key']
            password = self.get_password(password_key)

            if not password:
                logging.error(f"No se pudo obtener contraseña para {nvr['name']}")
                return False

            # Intentar conectar
            url = f"http://{ip}:80/ISAPI/System/status"
            response = self.session.get(
                url,
                auth=HTTPBasicAuth(username, password),
                timeout=5
            )

            if response.status_code == 200:
                logging.info(f"✓ {nvr['name']} ({ip}) - Conectado")
                return True
            else:
                logging.warning(f"✗ {nvr['name']} ({ip}) - Status {response.status_code}")
                return False

        except Exception as e:
            logging.error(f"✗ {nvr['name']} - Error: {str(e)[:60]}")
            return False

    def get_nvr_status(self, nvr):
        """Obtiene estado del NVR"""
        try:
            ip = nvr['ip']
            username = nvr['username']
            password_key = nvr['password_key']
            password = self.get_password(password_key)

            url = f"http://{ip}:80/ISAPI/System/status"
            response = self.session.get(
                url,
                auth=HTTPBasicAuth(username, password),
                timeout=5
            )

            if response.status_code == 200:
                # Parsear respuesta XML (simplificado)
                return {
                    'status': 'online',
                    'response': response.text[:200]
                }
            else:
                return {'status': 'offline', 'code': response.status_code}

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def monitor_all_nvrs(self):
        """Monitorea todos los NVRs"""
        logging.info("=" * 60)
        logging.info(f"MONITOREO HIKVISION: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("=" * 60)

        online_count = 0
        offline_count = 0

        for nvr in self.devices_config['hikvision_nvrs']:
            status = self.get_nvr_status(nvr)

            if status['status'] == 'online':
                logging.info(f"✓ {nvr['name']:40} | {nvr['ip']:15} | ONLINE  | {nvr['modelo']}")
                online_count += 1
            else:
                logging.warning(f"✗ {nvr['name']:40} | {nvr['ip']:15} | OFFLINE | {nvr['modelo']}")
                offline_count += 1

        logging.info("=" * 60)
        logging.info(f"Resumen: {online_count} ONLINE | {offline_count} OFFLINE | Total: {len(self.devices_config['hikvision_nvrs'])}")
        logging.info("=" * 60)

    def test_all_connections(self):
        """Prueba conexión a todos los NVRs"""
        logging.info("PRUEBAS DE CONEXIÓN HIKVISION")
        logging.info("=" * 60)

        for nvr in self.devices_config['hikvision_nvrs']:
            self.test_connection(nvr)

        logging.info("=" * 60)

if __name__ == "__main__":
    monitor = HikvisionMonitor()

    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        monitor.test_all_connections()
    else:
        monitor.monitor_all_nvrs()
