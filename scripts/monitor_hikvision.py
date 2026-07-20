#!/usr/bin/env python3
"""
TEKOSECURE - Monitor Hikvision (Integrado con Supabase)
Monitorea estado de NVRs y guarda en BD en tiempo real
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
from supabase_client import supabase

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
            self.session.verify = False
            self.nvr_previous_state = {}
            logging.info(f"Monitor Hikvision inicializado - {len(self.devices_config['hikvision_nvrs'])} NVRs")
        except Exception as e:
            logging.error(f"Error inicializando monitor Hikvision: {e}")
            sys.exit(1)

    def get_password(self, password_key):
        """Obtiene contraseña desencriptada"""
        import os
        from dotenv import load_dotenv

        env_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env.supabase')
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

    def check_nvr_status(self, nvr):
        """Comprueba estado del NVR"""
        try:
            ip = nvr['ip']
            username = nvr['username']
            password_key = nvr['password_key']
            password = self.get_password(password_key)

            if not password:
                logging.error(f"No se pudo obtener contraseña para {nvr['name']}")
                return {'status': 'error', 'ip': ip}

            url = f"http://{ip}:80/ISAPI/System/status"
            response = self.session.get(
                url,
                auth=HTTPBasicAuth(username, password),
                timeout=5
            )

            if response.status_code == 200:
                return {'status': 'online', 'ip': ip, 'response_time': response.elapsed.total_seconds()}
            else:
                return {'status': 'offline', 'ip': ip, 'code': response.status_code}

        except requests.exceptions.Timeout:
            return {'status': 'timeout', 'ip': ip}
        except Exception as e:
            return {'status': 'error', 'ip': ip, 'error': str(e)[:50]}

    def record_hikvision_event(self, nvr, status_result):
        """Registra evento en Supabase"""
        try:
            event_data = {
                'nvr_id': nvr['id'],
                'nvr_name': nvr['name'],
                'nvr_ip': nvr['ip'],
                'event_type': 'STATUS_CHECK',
                'status': status_result['status'].upper(),
                'model': nvr['modelo'],
                'port_count': nvr['puertos'],
                'location': nvr['ubicacion'],
                'details': json.dumps(status_result)
            }

            # Registrar en Supabase
            if supabase:
                supabase.log_hikvision_event(event_data)
            else:
                logging.warning("Supabase no disponible, guardando solo en log")

            # Detectar cambios de estado
            key = nvr['ip']
            old_status = self.nvr_previous_state.get(key, 'unknown')
            new_status = status_result['status']

            if old_status != new_status and old_status != 'unknown':
                # Estado cambió - crear alerta
                logging.warning(f"⚠️ {nvr['name']}: {old_status.upper()} → {new_status.upper()}")

                # Registrar alerta en Supabase
                if supabase:
                    supabase.log_attack({
                        'attack_type': 'NVR_STATUS_CHANGE',
                        'source_ip': nvr['ip'],
                        'severity': 'HIGH' if new_status == 'offline' else 'MEDIUM',
                        'details': f"NVR {nvr['name']} cambió de {old_status} a {new_status}",
                        'mikrotik_ip': '192.168.13.100',
                        'status': 'ACTIVE'
                    })

            self.nvr_previous_state[key] = new_status

        except Exception as e:
            logging.error(f"Error registrando evento: {e}")

    def monitor_all_nvrs(self):
        """Monitorea todos los NVRs y registra en BD"""
        logging.info("=" * 70)
        logging.info(f"MONITOREO HIKVISION: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("=" * 70)

        online_count = 0
        offline_count = 0
        error_count = 0

        for nvr in self.devices_config['hikvision_nvrs']:
            status = self.check_nvr_status(nvr)

            # Registrar en BD
            self.record_hikvision_event(nvr, status)

            # Estadísticas
            if status['status'] == 'online':
                logging.info(f"✓ {nvr['name']:40} | {nvr['ip']:15} | ONLINE  | {nvr['modelo']:20} | {nvr['puertos']} puertos")
                online_count += 1
            elif status['status'] == 'offline':
                logging.warning(f"✗ {nvr['name']:40} | {nvr['ip']:15} | OFFLINE | {nvr['modelo']:20} | {nvr['puertos']} puertos")
                offline_count += 1
            else:
                logging.error(f"E {nvr['name']:40} | {nvr['ip']:15} | ERROR   | {status.get('error', 'unknown')}")
                error_count += 1

        logging.info("=" * 70)
        logging.info(f"RESUMEN: {online_count} ONLINE | {offline_count} OFFLINE | {error_count} ERRORES | Total: {len(self.devices_config['hikvision_nvrs'])}")
        logging.info(f"SUPABASE: Registrando eventos en BD en tiempo real")
        logging.info("=" * 70)

    def continuous_monitoring(self, interval=60):
        """Monitoreo continuo"""
        import time

        logging.info(f"Iniciando monitoreo continuo (intervalo: {interval}s)")

        try:
            while True:
                self.monitor_all_nvrs()
                time.sleep(interval)
        except KeyboardInterrupt:
            logging.info("Monitoreo detenido por usuario")
        except Exception as e:
            logging.error(f"Error en monitoreo continuo: {e}")

if __name__ == "__main__":
    monitor = HikvisionMonitor()

    if len(sys.argv) > 1:
        if sys.argv[1] == '--once':
            monitor.monitor_all_nvrs()
        elif sys.argv[1] == '--continuous':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            monitor.continuous_monitoring(interval)
    else:
        # Por defecto: una sola ejecución
        monitor.monitor_all_nvrs()
